from schemas.product import CategorySchema
from typing import Optional, List
from slugify import slugify
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from libs.deps import get_admin, get_superadmin
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update, delete
from datetime import datetime, timezone, timedelta
from schemas.admin.product import AdminCategorySchema, CategorySchemaIn, CategoryUpdateSchema
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
from libs.redis import redis


router = APIRouter(prefix="/products")
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
                        options=attr_key.options,
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
                                options=attr_key.options,
                            )
                        )
                new_category.sub_categories.append(sub_c)

        db.add(new_category)
        await db.commit()
        await redis.delete("cat:all")
        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error occurred!",
        )


@c_router.get("/all", response_model=List[CategorySchema])
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


@c_router.get("/{slug}", response_model=AdminCategorySchema)
@limiter.limit("200/minute", error_message="Too many request, try again later")
async def admin_get_single_category(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_admin),
):
    condition = (
        Category.id == int(slug)
        if slug.isdigit()
        else func.lower(Category.slug) == slug.lower().strip()
    )
    stmt = (
        select(Category)
        .options(
            selectinload(Category.sub_categories).options(
                selectinload(Category.attributes), selectinload(Category.sub_categories)
            ),
            selectinload(Category.attributes),
        )
        .where(condition)
    )

    res = (await db.scalars(stmt)).first()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return res


@c_router.put("/{category_id}")
@limiter.limit("20/minute", error_message="Too many request, try again later")
async def update_product_category(
    request: Request,
    category_id: int,
    body: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_admin),
):
    stmt = (
        select(Category)
        .options(
            selectinload(Category.attributes),
            selectinload(Category.sub_categories).options(selectinload(Category.attributes)),
        )
        .where(Category.id == category_id)
    )
    category = (await db.scalars(stmt)).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    if body.name and body.name.strip():
        category.name = body.name.lower().strip()
        category.slug = slugify(category.name, lowercase=True)

    if body.attributes is not None:
        # Clear existing attributes and re-add
        for attr in list(category.attributes):
            await db.delete(attr)

        for attr_key in body.attributes:
            category.attributes.append(
                AttributeKey(
                    name=attr_key.name.lower(),
                    form_type=attr_key.form_type,
                    required=attr_key.required,
                    options=attr_key.options,
                )
            )

    if body.sub_categories is not None:
        # Create new subcategories if provided
        for sub_cat in body.sub_categories:
            sub_name = sub_cat.name.lower().strip()
            sub_slug = slugify(sub_name, lowercase=True)
            new_sub = Category(name=sub_name, slug=sub_slug)

            if sub_cat.attributes:
                for attr_key in sub_cat.attributes:
                    new_sub.attributes.append(
                        AttributeKey(
                            name=attr_key.name.lower(),
                            form_type=attr_key.form_type,
                            required=attr_key.required,
                            options=attr_key.options,
                        )
                    )
            category.sub_categories.append(new_sub)

    await db.commit()
    await redis.delete("cat:all")
    return {"success": True}


@c_router.delete("/{category_id}")
@limiter.limit("20/minute", error_message="Too many request, try again later")
async def delete_product_category(
    request: Request,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_admin),
):
    stmt = (
        select(Category)
        .options(
            selectinload(Category.attributes),
            selectinload(Category.sub_categories).options(selectinload(Category.attributes)),
        )
        .where(Category.id == category_id)
    )
    category = (await db.scalars(stmt)).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Delete attributes and subcategories
    for attr in category.attributes:
        await db.delete(attr)

    for sub in category.sub_categories:
        for sub_attr in sub.attributes:
            await db.delete(sub_attr)
        await db.delete(sub)

    await db.delete(category)
    await db.commit()
    await redis.delete("cat:all")
    return {"success": True}

