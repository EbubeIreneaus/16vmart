from pydantic import TypeAdapter
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    Request,
)
from libs.deps import get_store
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.store.entity import StoreSchema
from schemas.store.cat import AttrRsp, CategoryResp
from models.product import Category
from sqlalchemy.orm import selectinload
from libs.limiter import limiter
from libs.redis import redis

router = APIRouter(prefix="/{store_id}/cat", tags=["Stores", "Category"])


@router.get("/all", response_model=List[CategoryResp])
async def get_categories_for_store(
    request: Request,
    store_id: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    resp_list = TypeAdapter(List[CategoryResp])
    cache = await redis.get("store:cat:all")
    if cache:
        return resp_list.validate_json(cache)
    stmt = (
        select(Category)
        .options(selectinload(Category.sub_categories))
        .where(Category.parent_id == None)
    )

    result = (await db.scalars(stmt)).all()
    json = resp_list.dump_json(result)
    await redis.set("store:cat:all", json, ex=3600)
    return result

@router.get("/attr/{catId}", response_model=List[AttrRsp])
async def get_category_attributes(
    request: Request,
    store_id: str,
    catId: int,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    category = await db.scalar(
        select(Category)
        .options(
            selectinload(Category.parent).options(selectinload(Category.attributes)),
            selectinload(Category.attributes)
        )
        .where(Category.id == catId)
    )


    attributes = [x for x in category.attributes if len(category.attributes)>0]
    if category.parent and len(category.parent.attributes) > 0:
        attributes.extend(
            [x for x in category.parent.attributes]
        )

    return attributes
