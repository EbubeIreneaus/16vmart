import re
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request, Query
from models.user import Store
from libs.limiter import limiter
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from schemas.product import ProductResponse, MiniProductResponse, CONDITION
from schemas.store.entity import STORE_STATUS
from models.product import Category, Product, ProductAttribute
from sqlalchemy.orm import selectinload, aliased
from libs.redis import redis
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(prefix="/products")


@router.get("/filter", response_model=Page[MiniProductResponse])
async def filter_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    condition: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    ParentCategory = aliased(Category)

    stmt = (
        select(Product)
        .join(Product.store)
        .join(Product.category)
        .outerjoin(ParentCategory, Category.parent)
        .options(
            selectinload(Product.images),
            selectinload(Product.category),
            selectinload(Product.store),
        )
        .where(
            Product.available == True,
            Product.deleted == False,
            Store.status == STORE_STATUS.ACTIVE,
        )
    )

    if sub_category and sub_category.strip() and sub_category.lower().strip() != "all":
        stmt = stmt.where(func.lower(Category.slug) == sub_category.lower().strip())
    elif category and category.strip() and category.lower().strip() != "all":
        stmt = stmt.where(
            or_(
                func.lower(ParentCategory.slug) == category.lower().strip(),
                func.lower(Category.slug) == category.lower().strip(),
            )
        )

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    if condition and condition.strip() and condition.lower().strip() != "all":
        c_str = condition.lower().strip()
        if c_str in ["brand new", "new"]:
            stmt = stmt.where(Product.condition == CONDITION.NEW)
        elif c_str in ["used"]:
            stmt = stmt.where(Product.condition == CONDITION.USED)

    if q and q.strip() and len(q.strip()) >= 3:
        search_term = [re.sub(r"[^\w]", "", t) for t in q.split() if t]
        search_term = [t for t in search_term if t]
        if search_term:
            search_query = func.to_tsquery("english", " | ".join(f"{t}:*" for t in search_term))
            search_vector = func.to_tsvector(
                "english",
                func.coalesce(Product.name, " ") + " " + func.coalesce(Product.description, " "),
            )
            rank = func.ts_rank(search_vector, search_query)
            stmt = stmt.where(search_vector.op("@@")(search_query)).order_by(rank.desc())
    else:
        stmt = stmt.order_by(Product.id.desc())

    result = await paginate(db, stmt)
    return result


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

    search_term = [re.sub(r"[^\w]", "", t) for t in s.split() if t]
    search_term = [t for t in search_term if t]
    search_query = func.to_tsquery("english", " | ".join(f"{t}:*" for t in search_term))

    search_vector = func.to_tsvector(
        "english",
        func.coalesce(Product.name, " ") + " " + func.coalesce(Product.description),
    )
    search_query = func.to_tsquery("english", " | ".join(search_term))

    rank = func.ts_rank(search_vector, search_query)

    stmt = (
        select(Product)
        .join(Product.store)
        .options(selectinload(Product.images))
        .where(
            search_vector.op("@@")(search_query),
            Product.available == True,
            Store.status == STORE_STATUS.ACTIVE,
        )
        .order_by(rank.desc())
    )
    result = await paginate(db, stmt)

    return result


@router.get("/{slug}", response_model=ProductResponse)
async def get_single_product(slug: str, db: AsyncSession = Depends(get_db)):
    _slug = slug.lower().strip()
    cache = await redis.get(f"product:{_slug}")
    if cache:
        return ProductResponse.model_validate_json(cache)
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

    json_string = ProductResponse.model_validate(_product).model_dump_json()
    await redis.set(f"product:{_slug}", json_string, ex=86400)
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
