from typing import Optional, List
from slugify import slugify
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from libs.deps import get_admin, get_superadmin
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update, delete
from datetime import datetime, timezone, timedelta
from schemas.admin.product import AdminCategorySchema, CategorySchemaIn
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
from libs.limiter import limiter

router = APIRouter(prefix="/products", tags=["Admin", "Products"])
c_router = APIRouter(prefix="/cat", tags=["Admin", "Categories"])


@c_router.post("/create-category")
@limiter.limit("20/minute", error_message="Too many request, try again later")
async def create_product_category(
    request: Request,
    body: CategorySchemaIn,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_admin),
):
    try:
        category_name = body.name.lower()
        existing_category = await db.scalar(
            select(Category).where(func.lower(Category.name) == category_name)
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Conflic category name"
            )

        new_ct_slug = slugify(category_name, lowercase=True)
        new_category = Category(name=category_name, slug=new_ct_slug)

        if body.attributes:
            for attr_key in body.attributes:
                new_category.attributes.append(
                    AttributeKey(
                        name=attr_key.name.lower(),
                        form_type=attr_key.form_type,
                        required=attr_key.required,
                    )
                )

        # Implementing one level sub_category
        if body.sub_categories:

            requested_slugs = [
                slugify(sub.name.lower(), lowercase=True) for sub in body.sub_categories
            ]
            like_conditions = [
                Category.slug.like(f"{slug}%") for slug in requested_slugs
            ]

            stmt = select(Category.slug).where(or_(*like_conditions))

            result = await db.execute(stmt)
            existing_slugs = {row[0] for row in result.all()}

            for sub_category in body.sub_categories:

                name = sub_category.name.lower()
                base_slug = slugify(name, lowercase=True)
                slug_index = 1
                slug = base_slug

                while slug in existing_slugs:
                    slug = f"{base_slug}-{slug_index}"
                    slug_index += 1

                existing_slugs.add(slug)
                sub_c = Category(name=name, slug=slug)

                if sub_category.attributes:
                    for attr_key in sub_category.attributes:
                        sub_c.attributes.append(
                            AttributeKey(
                                name=attr_key.name.lower(),
                                form_type=attr_key.form_type,
                                required=attr_key.required,
                            )
                        )
                new_category.sub_categories.append(sub_c)

        db.add(new_category)
        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknow server error occured!",
        )


@c_router.get("/all", response_model=List[AdminCategorySchema])
@limiter.limit("200/minute", error_message="Too many request, try again later")
async def admin_get_all_category(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_admin),
):
    stmt = (
        select(Category)
        .options(
            selectinload(Category.sub_categories).options(
                selectinload(Category.attributes), selectinload(Category.sub_categories)
            ),
            selectinload(Category.attributes),
        )
        .where(Category.parent_id == None)
    )

    res = (await db.scalars(stmt)).all()
    return res


@c_router.get("/{slug}", response_model=List[AdminCategorySchema])
@limiter.limit("200/minute", error_message="Too many request, try again later")
async def admin_get_single_category(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_admin),
):
    stmt = (
        select(Category)
        .options(
            selectinload(Category.sub_categories).options(
                selectinload(Category.attributes), selectinload(Category.sub_categories)
            ),
            selectinload(Category.attributes),
        )
        .where(func.lower(Category.slug) == slug.lower().strip())
    )

    res = await db.scalars(stmt)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="category not found"
        )
    return res
