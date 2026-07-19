import re
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request, Query
from libs.deps import get_user
from schemas.user import UserShema
from schemas.shopping import WishlistIn, WishlistOut
from schemas.product import ProductResponse
from models.shopping import Wishlist
from models.product import Product
from libs.limiter import limiter
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from libs.redis import redis
from sqlalchemy import func
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(prefix="/wishlists", tags=["Wishlist"])


@router.post("")
async def create_wishlist(
    body: WishlistIn,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    slug = body.product_id.lower().strip()
    cached_product = await redis.get(f"product:{slug}")
    product = None
    if cached_product:
        product = ProductResponse.model_validate_json(cached_product)
    else:
        product = await db.scalar(
            select(Product).where(
                func.lower(Product.slug) == slug, Product.deleted == False
            )
        )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found"
        )

    existing = await db.scalar(
        select(Wishlist).where(
            Wishlist.product_id == product.id, Wishlist.user_id == user.id
        )
    )

    if existing:
        return {"success": True}

    wishlist = Wishlist(product_id=product.id, user_id=user.id)
    db.add(wishlist)
    await db.flush()

    return {"success": True}

@router.get("", response_model=Page[WishlistOut])
async def create_wishlist(
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Wishlist)
        .join(Wishlist.product)
        .options(selectinload(Wishlist.product))
        .where(Wishlist.user_id == user.id, Product.deleted == False)
    )

    result = await paginate(db, stmt)
    return result

@router.get("/ids", response_model=List[str])
async def create_wishlist(
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Wishlist).distinct()
        .options(selectinload(Wishlist.product))
        .where(Wishlist.user_id == user.id, Product.deleted == False)
    )

    result = (await db.scalars(stmt)).all()
    res = [x.product.slug.lower() for x in result]
    return res



@router.delete("/{product_id}")
async def create_wishlist(
    product_id: str,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    slug = product_id.lower().strip()
    wishlist = await db.scalar(
        select(Wishlist).options(
            selectinload(Wishlist.product)
        ).where(func.lower(Product.slug) == slug, Wishlist.user_id == user.id)
    ) 
    if not wishlist:
        return {"success": True}
    
    await db.delete(wishlist)
    return {"success": True}
