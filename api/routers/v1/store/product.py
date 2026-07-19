from datetime import datetime, timezone
import re
from typing import Optional, List
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from slugify import slugify
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
    HTTPException,
    Header,
    Request,
    UploadFile,
    File,
)
from schemas.product import FormTypeLiteral
from libs.deps import get_store
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update, delete
from schemas.store.product import (
    ProductSchemaIn,
    ProductSchemaUpdate,
    MiniProductOut,
    SingleProductOut,
)
from schemas.user import UserShema
from schemas.store.entity import StoreSchema
from models.product import (
    Category,
    AttributeKey,
    ProductAttribute,
    ProductImages,
    Product,
)
from models.user import Store
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from libs.limiter import limiter
from libs.redis import redis
from libs.cloudinary import cloudinary, cloudinary_uploader
import asyncio
from settings import setting

router = APIRouter(prefix="/{store_id}/products", tags=["Stores", "Products"])


@router.post("/")
async def create_product(
    request: Request,
    body: ProductSchemaIn,
    store_id: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        name = body.name.lower().strip()
        base_slug = slugify(name)
        slug_index = 1
        slug = base_slug

        while True:
            existing_slug = await db.scalar(
                select(Product).where(func.lower(Product.slug) == slug)
            )
            if existing_slug:
                slug = f"{base_slug}-{slug_index}"
                slug_index += 1
            else:
                break

        category = await db.scalar(
            select(Category)
            .options(
                selectinload(Category.attributes),
                selectinload(Category.parent).options(
                    selectinload(Category.attributes)
                ),
            )
            .where(Category.id == body.category_id)
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid product category",
            )

        n_product = Product(
            name=name,
            slug=slug,
            price=body.price,
            description=body.description,
            available=body.available,
            category=category,
            store_id=store.id,
        )

        for attribute in body.attributes:

            attr_form_type = [
                x.form_type
                for x in category.attributes
                if x.id == attribute.attribute_id
            ]
            if category.parent:
                if len(category.parent.attributes) > 0:
                    attr_form_type.extend(
                        [
                            x.form_type
                            for x in category.parent.attributes
                            if x.id == attribute.attribute_id
                        ]
                    )

            if len(attr_form_type) < 1:

                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Invalid product attribute submited",
                )

            attr = ProductAttribute(
                attribute_id=attribute.attribute_id,
            )
            form_type: FormTypeLiteral = attr_form_type[0]
            value = attribute.value
            if form_type == "text" or form_type == "radio":
                attr.text_value = value
            elif form_type == "boolean":
                attr.boolean_value = value
            elif form_type == "number":
                attr.number_value = value
            elif form_type == "date":
                attr.date_value = value
            elif form_type == "multiple":
                attr.json_value = value
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="product attribute error",
                )
            n_product.attributes.append(attr)

        db.add(n_product)
        await db.flush()

        return {"success": True, "product_id": n_product.id}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )


@router.patch("/image/{product_id}")
async def update_product_image(
    request: Request,
    files: List[UploadFile],
    store_id: str,
    product_id: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        slug = product_id.lower().strip()
        product = await db.scalar(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                func.lower(Product.slug) == slug,
                Product.store_id == store.id,
                Product.deleted == False,
            )
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing product"
            )

        urls = []
        for file in files:
            name = f"{product.slug}-{datetime.now().microsecond}".lower()

            res = await asyncio.to_thread(
                cloudinary_uploader.upload,
                file.file,
                public_id=name,
                overwrite=False,
                unique_filename=True,
                folder=f"{setting.IMAGE_FOLDER}/product",
            )
            if res["secure_url"]:
                product.images.append(ProductImages(name=name, src=res["secure_url"]))

                urls.append({"src": res["secure_url"], "name": name})

        await redis.delete(f"product:{slug}")
        return {"success": True, "data": urls}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )


@router.delete("/image/{name}/{product_id}")
async def delete_product_image(
    request: Request,
    product_id: str,
    store_id: str,
    name: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        slug = product_id.lower().strip()
        image = await db.scalar(
            select(ProductImages)
            .options(
                selectinload(ProductImages.product).options(selectinload(Product.store))
            )
            .where(ProductImages.name == name, func.lower(Product.slug) == slug)
        )

        if not image or image.product.store_id != store.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing image or unathorize delete",
            )
        res = await asyncio.to_thread(
            cloudinary_uploader.destroy,
            public_id=f"{setting.IMAGE_FOLDER}/products/{name}",
            invalidate=True,
        )

        await db.delete(image)
        await redis.delete(f"product:{slug}")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )

@router.patch("/{product_id}")
async def edit_product(
    request: Request,
    store_id: str,
    product_id: str,
    body: ProductSchemaUpdate,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        slug = product_id.lower().strip()
        data = body.model_dump(exclude_unset=True)
        stmt = (
            update(Product)
            .where(
                func.lower(Product.slug) == slug,
                Product.store_id == store.id,
                Product.deleted == False,
            )
            .values(**data)
        )
        result = await db.execute(stmt)
        await db.flush()
        await redis.delete(f"product:{slug}")
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )

@router.delete("/{product_id}")
async def delete_product(
    request: Request,
    store_id: str,
    product_id: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    slug = product_id.lower().strip()
    now = datetime.now(timezone.utc)
    stmt = (
        update(Product)
        .where(
            func.lower(Product.slug) == slug,
            Product.store_id == store.id,
            Product.deleted == False,
        )
        .values(deleted=True, deleted_at=now, available=False)
    )
    await db.execute(stmt)
    await redis.delete(f"product:{slug}")

    return {"success": True}

@router.get("/all", response_model=Page[MiniProductOut])
async def get_all_product(
    request: Request,
    store_id: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        stmt = (
            select(Product)
            .options(selectinload(Product.store))
            .where(func.lower(Store.slug) == store.slug, Product.deleted == False)
        )
        result = await paginate(db, stmt)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )

@router.get("/search", response_model=Page[MiniProductOut])
async def store_search_product(
    store: StoreSchema = Depends(get_store),
    s: str = Query(min_length=3),
    db: AsyncSession = Depends(get_db),
):

    search_term = [re.sub(r"[^\w]", "", t) for t in s.split() if t]
    search_term = [t for t in search_term if t]
    search_query = func.to_tsquery("english", " | ".join(f"{t}:*" for t in search_term))

    search_vector = func.to_tsvector(
        "english",
        Product.name,
    )
    search_query = func.to_tsquery("english", " | ".join(search_term))

    rank = func.ts_rank(search_vector, search_query)

    stmt = (
        select(Product)
        .options(selectinload(Product.store))
        .where(
            search_vector.op("@@")(search_query),
            func.lower(Store.slug) == store.slug.lower(),
            Product.deleted == False,
        )
        .order_by(rank.desc())
    )
    result = await paginate(db, stmt)

    return result


@router.get("/{slug}", response_model=SingleProductOut)
async def store_get_single_product(
    slug: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    _slug = slug.lower().strip()

    stmt = (
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.store),
            selectinload(Product.attributes).options(
                selectinload(ProductAttribute.attribute)
            ),
        )
        .where(
            func.lower(Store.slug) == store.slug.lower(),
            func.lower(Product.slug) == _slug,
            Product.deleted == False,
        )
    )

    product = await db.scalar(stmt)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    attributes = product.attributes

    _product = MiniProductOut.model_validate(product).model_dump()
    _attributes = []

    for attr in attributes:
        obj = {"name": attr.attribute.name}
        form_type = attr.attribute.form_type.lower()
        if form_type in ["text", "select", "radio"]:
            obj["type"] = "text"
            obj["value"] = attr.text_value
        elif form_type == "boolean":
            obj["type"] = "boolean"
            obj["value"] = attr.boolean_value
        elif form_type == "date":
            obj["type"] = "date"
            obj["value"] = attr.date_value
        elif form_type == "multiple":
            obj["type"] = "list"
            obj["value"] = attr.json_value
        elif form_type == "number":
            obj["type"] = "number"
            obj["value"] = attr.number_value
        else:
            continue

        _attributes.append(obj)

    _product["attributes"] = _attributes

    return _product
