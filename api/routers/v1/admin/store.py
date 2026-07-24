import re
from typing import Literal, Optional, List
from fastapi import APIRouter, Depends, Query, status, HTTPException, Header, Request
from models.product import Product
from models.user import Store
from libs.deps import get_admin, get_superadmin
from libs.redis import redis
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update, delete
from schemas.admin.store import MiniStoreOut, StoreOut, StatusUpdate
from schemas.user import ROLE, STATUS, UserShema
from schemas.store.entity import STORE_STATUS
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from libs.limiter import limiter
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

router = APIRouter(prefix="/stores")


@router.get("/all", response_model=Page[MiniStoreOut])
async def get_all_store(
    s: Optional[STORE_STATUS | Literal["all"]] = "all",
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Store).options(selectinload(Store.user))

    if s != "all":
        stmt = stmt.where(Store.status == s)

    stmt = stmt.order_by(Store.id.desc())
    result = await paginate(db, stmt)
    return result

@router.get("/search", response_model=Page[MiniStoreOut])
async def admin_search_product(
    admin: UserShema = Depends(get_admin),
    s: str = Query(min_length=3),
    db: AsyncSession = Depends(get_db),
):

    search_term = [re.sub(r"[^\w]", "", t) for t in s.split() if t]
    search_term = [t for t in search_term if t]
    search_query = func.to_tsquery("english", " | ".join(f"{t}:*" for t in search_term))

    search_vector = func.to_tsvector(
        "english",
        func.coalesce(Store.name, " ") + " " + func.coalesce(Store.industry),
    )
    search_query = func.to_tsquery("english", " | ".join(search_term))

    rank = func.ts_rank(search_vector, search_query)

    stmt = (
        select(Store)
        .where(
            search_vector.op("@@")(search_query)
        )
        .order_by(rank.desc())
    )
    result = await paginate(db, stmt)

    return result

@router.get("/{slug}", response_model=StoreOut)
async def get_all_store(
    slug: str, admin: UserShema = Depends(get_admin), db: AsyncSession = Depends(get_db)
):

    stmt = (
        select(Store)
        .options(selectinload(Store.user))
        .where(func.lower(Store.slug) == slug.lower())
    )

    result = await db.scalar(stmt)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )

    return result

@router.post("/update-status")
async def update_store_status(
    body: StatusUpdate,
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    slug = body.slug.lower()
    store = await db.scalar(
        select(Store)
        .options(selectinload(Store.user))
        .where(func.lower(Store.slug) == slug)
    )

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="store not found"
        )

    if store.status == body.status:
        return {"success": True, "data": body.status}

    if store.user.status != STATUS.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="store owner account is not active",
        )

    if store.status == STORE_STATUS.TERMINATED and admin.role != ROLE.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only superadmin can restore terminated store",
        )

    store.status = body.status

    await db.flush()
    return {"success": True, "data": store.status}
