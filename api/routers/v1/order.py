from datetime import datetime, timezone
import uuid
import secrets
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from models.user import Store
from libs.deps import get_user
from schemas.user import UserShema
from schemas.store.entity import STORE_STATUS
from schemas.shopping import BaseOrderMini, SingleOrderOut
from schemas.checkout import CheckoutIn
from models.shopping import Order, OrderProduct
from models.product import Product
from libs.limiter import limiter
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

router = APIRouter(prefix="/shopping", tags=["Checkout"])

client = stripe.StripeClient(setting.STRIPE_SECRET)

@router.post("/checkout")
async def checkout(
    request: Request,
    body: CheckoutIn,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
) -> BaseOrderMini:

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
        z = await db.scalar(select(Order).where(order_number == order_number))
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

    return order


@router.get("/orders")
async def get_orders(
    request: Request,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
) -> List[BaseOrderMini]:
    orders = await db.scalars(select(Order).where(Order.user_id == user.id))

    return orders.all()

@router.get("/order/{order_number}")
async def get_orders(
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
            selectinload(Order.items).options(selectinload(OrderProduct.product).options(
                selectinload(Product.images)
            )),
        )
        .where(Order.order_number == order_number, Order.user_id == user.id)
    )

    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order

def stripe_checkout():
    pass