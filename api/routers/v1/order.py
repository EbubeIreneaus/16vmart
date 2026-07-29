from datetime import datetime, timezone
import uuid
import secrets
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from models.user import Store
from libs.deps import get_user
from schemas.user import UserShema
from schemas.store.entity import STORE_STATUS
from schemas.shopping import ORDER_STATUS, BaseOrderMini, SingleOrderOut
from schemas.checkout import CheckoutIn
from models.shopping import Order, OrderProduct
from models.product import Product
from libs.limiter import limiter
from libs.logger import logger
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from libs.redis import redis
from routers.v1.user import create_address, get_address
from sqlalchemy import func
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
import stripe
from settings import setting
from bg_task.config import get_arq_pool


router = APIRouter(prefix="/shopping")

client = stripe.StripeClient(setting.STRIPE_SECRET)


@router.post("/checkout")
@limiter.limit("10/minute", error_message="Too many checkout attempts, please try again later")
async def checkout(
    request: Request,
    body: CheckoutIn,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    if len(body.items) < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot checkout empty cart list",
        )

    existing_order = await db.scalar(
        select(Order).where(Order.idompotent_key == body.idompotent_key)
    )

    if existing_order:
        if existing_order.user_id == user.id:
            return existing_order
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error occured, retry checkout",
            )

    product_ids = [x.product_id.lower().strip() for x in body.items]
    products = (
        await db.scalars(
            select(Product)
            .join(Product.store)
            .options(selectinload(Product.store))
            .where(
                func.lower(Product.slug).in_(product_ids),
                Product.available == True,
                Product.deleted == False,
                Store.status == STORE_STATUS.ACTIVE,
            )
        )
    ).all()

    key_value = {p.slug.lower(): p for p in products}

    cart = [
        OrderProduct(
            product_id=key_value[item.product_id.lower()].id,
            unit_price=key_value[item.product_id.lower()].price,
            quantity=item.quantity,
        )
        for item in body.items
    ]

    total_price = sum([x.unit_price * x.quantity for x in cart])
    order_number = None
    while True:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        random_digits = secrets.randbelow(900000) + 100000
        order_number = f"ORD-{date_str}-{random_digits}"
        z = await db.scalar(select(Order).where(Order.order_number == order_number))
        if not z:
            break

    address_id = None
    if isinstance(body.delivery_address, uuid.UUID):
        address = await get_address(
            db=db, user=user, address_id=body.delivery_address, request=request
        )
        address_id = address.address_id
    else:
        address = await create_address(
            db=db, user=user, body=body.delivery_address, request=request
        )
        address_id = address.address_id

    order = Order(
        order_number=order_number,
        user_id=user.id,
        items=cart,
        idompotent_key=body.idompotent_key,
        delivery_addr_id=address_id,
    )

    db.add(order)
    await db.flush()
    stripe_session = await stripe_checkout(order, user)
    await redis.delete(f"16vmart:cart:{user.id}")
    logger.info(f"Order created successfully: {order_number} for user {user.id}")
    return {"success": True, "url": stripe_session.url}


@router.get("/orders")
@limiter.limit("60/minute", error_message="Too many requests, try again later")
async def get_orders(
    request: Request,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
) -> List[BaseOrderMini]:
    orders = await db.scalars(select(Order).where(Order.user_id == user.id))

    return orders.all()


@router.get("/order/{order_number}")
@limiter.limit("60/minute", error_message="Too many requests, try again later")
async def get_order_by_number(
    request: Request,
    order_number: str,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
) -> SingleOrderOut:
    order = await db.scalar(
        select(Order)
        .join(Order.delivery_address)
        .join(Order.items)
        .options(
            selectinload(Order.delivery_address),
            selectinload(Order.items).options(
                selectinload(OrderProduct.product).options(
                    selectinload(Product.images), selectinload(Product.category)
                )
            ),
        )
        .where(Order.order_number == order_number, Order.user_id == user.id)
    )

    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order


async def stripe_checkout(order: SingleOrderOut, user: UserShema):
    items = order.items
    line_item = [
        {
            "price_data": {
                "currency": "usd",
                "unit_amount": int(item.unit_price * 100),
                "product_data": {"name": item.product.name},
            },
            "quantity": item.quantity,
        }
        for item in items
    ]
    try:
        session = await client.v1.checkout.sessions.create_async(
            params={
                "line_items": line_item,
                "mode": "payment",
                "currency": "usd",
                "customer_creation": "if_required",
                "client_reference_id": order.order_number,
                "cancel_url": f"{setting.APP_URL}/checkout/cancel?order_number={order.order_number}",
                "success_url": f"{setting.APP_URL}/checkout/success?order_number={order.order_number}",
                "customer_email": user.email,
                "metadata": {"customer_fullname": user.fullname},
            },
            options={"idempotency_key": str(order.idompotent_key)},
        )
        return session
    except stripe.error.StripeError as e:
        logger.exception(f"Stripe checkout session error for order {order.order_number}: {e}")
        raise HTTPException(
            status.HTTP_424_FAILED_DEPENDENCY, detail="stripe payment error"
        )


@router.post("/stripe-webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, setting.STRIPE_HOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as err:
        logger.warning(f"Invalid Stripe Webhook Signature: {err}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    arq = await get_arq_pool()
    logger.info(f"Stripe Webhook event received: {event['type']}")

    match event["type"]:
        case "checkout.session.completed":
            session = event["data"]["object"]
            order_number = session["client_reference_id"]
            await arq.enqueue_job("update_order", ORDER_STATUS.PROCESSING, order_number, _queue_name="16vmart")
            logger.info(f"Enqueued update_order job to PROCESSING for {order_number}")
        case "checkout.session.expired":
            session = event["data"]["object"]
            order_number = session["client_reference_id"]
            await arq.enqueue_job("update_order", ORDER_STATUS.CANCELLED, order_number, _queue_name="16vmart")
            logger.info(f"Enqueued update_order job to CANCELLED for {order_number}")
        case "charge.refunded":
            pass
        case "charge.dispute.created":
            pass
    return {"received": True}
