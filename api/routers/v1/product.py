import re
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request, Query
from models.user import Store
from libs.limiter import limiter
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.product import ProductResponse, MiniProductResponse
from schemas.store.entity import STORE_STATUS
from models.product import Category, Product, ProductAttribute
from sqlalchemy import func, and_
from sqlalchemy.orm import selectinload
from libs.redis import redis
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/feature", response_model=Page[MiniProductResponse])
async def fetch_featured_product(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Product)
        .distinct()
        .options(selectinload(Product.store), selectinload(Product.images))
        .where(
            and_(
                Product.available == True,
                Product.deleted == False,
                Store.status == STORE_STATUS.ACTIVE,
            )
        )
    )
    result = await paginate(db, stmt)
    return result

@router.get("/search", response_model=Page[MiniProductResponse])
async def search_product(
    s: str = Query(min_length=3), db: AsyncSession = Depends(get_db)
):

    search_term = [re.sub(r'[^\w]', '', t) for t in s.split() if t]
    search_term = [t for t in search_term if t] 
    search_query = func.to_tsquery("english", " | ".join(f"{t}:*" for t in search_term))

    search_vector = func.to_tsvector(
        "english",
        func.coalesce(Product.name, " ") + " " + func.coalesce(Product.description)
    )
    search_query = func.to_tsquery("english", " | ".join(search_term))

    rank = func.ts_rank(search_vector, search_query)

    stmt = select(Product).join(Product.store).options(
        selectinload(Product.images)
    ).where(
        search_vector.op('@@')(search_query),
        Product.available == True,
        Store.status == STORE_STATUS.ACTIVE
    ).order_by(rank.desc())
    result = await paginate(db, stmt)

    return result

@router.get("/{slug}", response_model=ProductResponse)
async def get_single_product(slug: str, db: AsyncSession = Depends(get_db)):
    _slug = slug.lower().strip()
    stmt = (
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes).options(
                selectinload(ProductAttribute.attribute)
            ),
            selectinload(Product.store),
            selectinload(Product.category),
        )
        .where(func.lower(Product.slug) == slug)
    )

    product = await db.scalar(stmt)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")

    _attributes = []

    attributes = product.attributes
    category = product.category

    _product = MiniProductResponse.model_validate(product).model_dump()
    for attr in attributes:
        obj = {
            "name": attr.attribute.name,
        }

        form_type = attr.attribute.form_type

        if form_type in ["text", "radio", "select"]:
            obj["type"] = "text"
            obj["value"] = attr.text_value
        elif form_type == "number":
            obj["type"] = "number"
            obj["value"] = attr.number_value
        elif form_type == "boolean":
            obj["type"] = "boolean"
            obj["value"] = attr.boolean_value
        elif form_type == "date":
            obj["type"] = "date"
            obj["value"] = attr.date_value
        elif form_type == "multiple":
            obj["type"] = "multiple"
            obj["value"] = attr.json_value
        else:
            continue

        _attributes.append(obj)

    _product["attributes"] = _attributes
    _product["category"] = category
    return _product


@router.get("/cat/{slug}", response_model=Page[MiniProductResponse])
async def get_product_by_category(slug: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Product)
        .join(Product.category)
        .join(Product.store)
        .options(
            selectinload(Product.images),
            selectinload(Product.category),
            selectinload(Product.store),
        )
        .where(
            func.lower(Category.slug) == slug.lower().strip(),
            Store.status == STORE_STATUS.ACTIVE,
        )
    )

    result = await paginate(db, stmt)
    return result


