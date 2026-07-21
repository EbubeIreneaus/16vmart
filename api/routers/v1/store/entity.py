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
from models.product import Product
from libs.deps import get_store, get_user
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update
from datetime import datetime, timezone
from schemas.user import UserShema, ROLE
from schemas.store.entity import (
    BaseStoreSchemaOut,
    StoreSchema,
    StoreSchemaIn,
    StoreSchemaUpdate,
    STORE_STATUS,
)
from models.user import Store, User
from sqlalchemy import func
from libs.limiter import limiter
from libs.redis import redis
from libs.cloudinary import cloudinary, cloudinary_uploader
import asyncio

router = APIRouter(prefix="/entity")

@router.post("")
async def create_store_profile(
    request: Request,
    body: StoreSchemaIn,
    _user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        business_name = body.name.strip()
        base_slug = slugify(business_name, lowercase=True, allow_unicode=True)
        slug = base_slug
        index = 1

        while True:
            existing_slug = await db.scalar(select(Store).where(Store.slug == slug))
            if existing_slug:
                slug = f"{base_slug}-{index}"
                index += 1
            else:
                break

        store = Store(
            **body.model_dump(exclude={"name", "logo"}),
            name=business_name,
            slug=slug,
            user_id=_user.id,
        )

        if _user.role != ROLE.SELLER:
            await db.execute(
                update(User).where(User.id == _user.id).values(role=ROLE.SELLER)
            )

        db.add(store)
        await db.flush()
        await redis.delete(f"user:{_user.id}")

        return {"success": True, "id": slug}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error, please try again later",
        )

@router.patch("/{store_id}/logo")
async def update_business_logo(
    request: Request,
    logo: UploadFile,
    store_id: str,
    _store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):

    store = await db.scalar(select(Store).where(Store.id == _store.id))
    res = await asyncio.to_thread(
        cloudinary_uploader.upload, logo.file, public_id=store.slug, overwrite=True
    )
    if res["secure_url"]:
        store.logo = res["secure_url"]
        return {"success": True, "data": res["secure_url"]}
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="third party service unavailable",
    )

@router.patch("/{store_id}")
async def update_store_profile(
    request: Request,
    body: StoreSchemaUpdate,
    store_id: str,
    _store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Store)
        .where(Store.id == _store.id)
        .values(**body.model_dump(exclude_unset=True))
    )
    return {"success": True}

@router.delete("/{store_id}")
async def delete_store_profile(
    request: Request,
    body: StoreSchemaUpdate,
    store_id: str,
    _store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    user = _store.user

    await db.execute(
        update(Store)
        .where(Store.id == _store.id)
        .values(deleted=True, deleted_at=now, status=STORE_STATUS.DEACTIVATED)
    )
    await db.execute(
        update(Product)
        .where(Product.store_id == _store.id)
        .values(deleted=True, deleted_at=now, available=False)
    )
    await redis.delete(f"store:{user.id}:{_store.slug}")
    return {"success": True, "date": _store.slug}  # return slug of the deleted account

@router.get('')
async def get_my_stores(
    request: Request,
    user: UserShema = Depends(get_user),
    db: AsyncSession = Depends(get_db),
) -> List[BaseStoreSchemaOut]:
    stmt = select(Store).where(Store.user_id == user.id, Store.deleted==False)
    results = await db.scalars(stmt)

    return results.all()

@router.get('/{store_id}')
async def get_my_stores(
    request: Request,
    store_id: str,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
) -> BaseStoreSchemaOut:
    return store