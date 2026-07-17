from typing import Optional, List
from pydantic import TypeAdapter
from slugify import slugify
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from libs.deps import get_admin, get_superadmin
from libs.limiter import limiter
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import not_, or_, select, update, delete
from datetime import datetime, timezone, timedelta
from schemas.product import BaseCategorySchema,  CategorySchemaResponse
from schemas.user import UserShema
from models.product import (
    Category,
    AttributeKey,
    ProductAttribute,
    ProductImages,
    Product,
)
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from libs.redis import redis

p_router = APIRouter(prefix="/products", tags=["Products"])  # product Router
c_router = APIRouter(prefix="/cat", tags=["Categories"])  # category router


@c_router.get("/all", response_model=List[CategorySchemaResponse])
@limiter.limit("300/hour", error_message="Too many request, try again later")
async def get_all_categories(request: Request, db: AsyncSession = Depends(get_db)):

    ResponseModel = TypeAdapter(List[CategorySchemaResponse])
    result = await redis.get("cat:all")
    if result:
        data = ResponseModel.validate_json(result)
        return data

    stmt = (
        select(Category)
        .options(
            selectinload(Category.sub_categories).options(
                selectinload(Category.sub_categories)
            ),
        )
        .where(Category.parent_id == None)
    )

    response = (await db.scalars(stmt)).all()
    if len(response) > 0:
        json_bytes = ResponseModel.dump_json(response)
        await redis.set("cat:all", json_bytes, ex=600)

    return response

@c_router.get("/{slug}", response_model=List[CategorySchemaResponse])
@limiter.limit("300/hour", error_message="Too many request, try again later")
async def get_single_category(request:Request, slug:str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Category)
        .options(
            selectinload(Category.sub_categories).options(
                selectinload(Category.sub_categories)
            ),
        )
        .where(func.lower(Category.slug) == slug.lower().strip())
    )

    response = await db.scalars(stmt)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="category not found"
        )
    return response
