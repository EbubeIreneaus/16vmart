import re
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request, Query
from pydantic import TypeAdapter
from models.user import Store
from schemas.store.entity import STORE_STATUS
from libs.deps import get_user
from schemas.user import UserShema
from schemas.product import MiniProductResponse
from schemas.cart import CartIn, CartOut
from models.product import Product
from libs.limiter import limiter
from libs.logger import logger
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from libs.redis import redis

router = APIRouter(prefix="/carts")

CartInList = TypeAdapter(List[CartIn])


@router.post("")
@limiter.limit("30/minute", error_message="Too many requests, try again later")
async def save_cart(request: Request, body: CartIn, user: UserShema = Depends(get_user)):
    slug = body.product_id.lower().strip()

    cartItems = []

    cache = await redis.get(f"16vmart:cart:{user.id}")

    if not cache:
        new_cart = CartIn(product_id=slug, quantity=body.quantity)
        cartItems.append(new_cart)
    else:
        carts = CartInList.validate_json(cache)
        cartItems = [x for x in carts if x.product_id != slug]
        cartItems.append(CartIn(product_id=slug, quantity=body.quantity))
    json_data = CartInList.dump_json(cartItems)
    await redis.set(f"16vmart:cart:{user.id}", json_data, ex=1209600)
    return {"success": True}


@router.delete("/{product_id}")
@limiter.limit("30/minute", error_message="Too many requests, try again later")
async def remove_cart_item(request: Request, product_id: str, user: UserShema = Depends(get_user)):
    slug = product_id.lower().strip()
    cache = await redis.get(f"16vmart:cart:{user.id}")
    if not cache:
        return {"success": True}

    cartItems = CartInList.validate_json(cache)
    new_cartItems = [x for x in cartItems if x.product_id != slug]

    json_data = CartInList.dump_json(new_cartItems)
    await redis.set(f"16vmart:cart:{user.id}", json_data, ex=1209600)
    return {"success": True}


@router.get("", response_model=List[CartOut])
@limiter.limit("60/minute", error_message="Too many requests, try again later")
async def get_cart_items(
    request: Request, user: UserShema = Depends(get_user), db: AsyncSession = Depends(get_db)
):
    cache = await redis.get(f"16vmart:cart:{user.id}")
    if not cache:
        return []
    cartItems = CartInList.validate_json(cache)
    if len(cartItems) < 1:
        return []
    slugs = [x.product_id.lower().strip() for x in cartItems]

    products = (
        await db.scalars(
            select(Product).distinct()
            .options(
                selectinload(Product.images),
                selectinload(Product.category),
                selectinload(Product.store),
            )
            .where(
                func.lower(Product.slug).in_(slugs),
                Product.available == True,
                Product.deleted == False,
                Store.status == STORE_STATUS.ACTIVE,
            )
        )
    ).all()

    key_value = {p.slug.lower().strip(): p for p in products}

    response = []

    for item in cartItems:
        item_product_slug = item.product_id.lower().strip()
        if item_product_slug in key_value:
            response.append(
                {"product": key_value[item_product_slug], "quantity": item.quantity}
            )

    return response


@router.get("/simple", response_model=List[CartIn])
@limiter.limit("60/minute", error_message="Too many requests, try again later")
async def get_simple_cart_items(
    request: Request, user: UserShema = Depends(get_user), db: AsyncSession = Depends(get_db)
):
    cache = await redis.get(f"16vmart:cart:{user.id}")
    if not cache:
        return []
    cartItems = CartInList.validate_json(cache)

    return cartItems
