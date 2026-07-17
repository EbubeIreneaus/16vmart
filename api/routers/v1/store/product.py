from typing import Optional, List
from slugify import slugify
from fastapi import (
    APIRouter,
    Depends,
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
from datetime import datetime, timezone, timedelta
from schemas.store.product import ProductSchemaIn, ProductSchemaUpdate
from schemas.user import UserShema
from schemas.store.entity import StoreSchema
from models.product import (
    Category,
    AttributeKey,
    ProductAttribute,
    ProductImages,
    Product,
)
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from libs.limiter import limiter
from libs.redis import redis
from libs.cloudinary import cloudinary, cloudinary_uploader
import asyncio
from settings import setting

router = APIRouter(prefix="/products", tags=["Stores", "Products"])


@router.post("/{store_id}")
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
            if form_type == "text":
                attr.text_value = value
            elif form_type == "boolean" or form_type == "radio":
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


@router.patch("/image/{store_id}/{productId}")
async def update_product_image(
    request: Request,
    files: List[UploadFile],
    store_id:str,
    productId: int,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        product = await db.scalar(
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.id == productId, Product.store_id == store.id)
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
        return {"success": True, "data": urls}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )


@router.delete("/image/{store_id}/{name}/{productId}")
async def delete_product_image(
    request: Request,
    productId: int,
    store_id: str,
    name: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        image = await db.scalar(
            select(ProductImages)
            .options(
                selectinload(ProductImages.product).options(
                    selectinload(Product.store)
                )
            )
            .where(ProductImages.name == name, ProductImages.product_id == productId)
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

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )


@router.patch("/{store_id}/{productId}")
async def edit_product(
    request: Request,
    store_id: str,
    productId: int,
    body: ProductSchemaUpdate,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = body.model_dump(exclude_unset=True)
        stmt = (
            update(Product)
            .where(Product.id == productId, Product.store_id == store.id)
            .values(**data)
        )
        result = await db.execute(stmt)
        await db.flush()
        return {'data': result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error, try again later",
        )


# @router.post("/create")
# async def create_product(
#     request: Request,
#     store: UserShema = Depends(get_store),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         pass
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Unknown server error, try again later",
#         )
