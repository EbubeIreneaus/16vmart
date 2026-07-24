from typing import Literal, Optional, List
from pydantic import EmailStr
from slugify import slugify
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from models.user import User
from libs.deps import get_admin, get_superadmin
from libs.redis import redis
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update, delete
from datetime import datetime, timezone, timedelta
from schemas.admin.user import RoleIn, StatusIn, MiniUserResp, UserResp
from schemas.user import ROLE, STATUS, UserShema
from schemas.store.entity import STORE_STATUS
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from libs.limiter import limiter
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

router = APIRouter(prefix="/users")


@router.get("/all", response_model=Page[MiniUserResp])
async def get_all_users(
    s: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: UserShema = Depends(get_admin),
):
    stmt = select(User)

    if s and s.strip() and s.lower().strip() != "all":
        statuses = [x.lower().strip() for x in s.split(",") if x.strip()]
        if statuses:
            stmt = stmt.where(func.lower(User.status).in_(statuses))

    stmt = stmt.order_by(User.id.desc())
    result = await paginate(db, stmt)
    return result


@router.get("/{email}", response_model=UserResp)
async def get_all_users(
    email: EmailStr,
    db: AsyncSession = Depends(get_db),
    admin: UserShema = Depends(get_admin),
):
    stmt = (
        select(User)
        .options(selectinload(User.sessions), selectinload(User.stores))
        .where(func.lower(User.email) == email.lower())
    )
    result = await db.scalar(stmt)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result

@router.post("/change-status")
async def get_all_users(
    body: StatusIn,
    db: AsyncSession = Depends(get_db),
    admin: UserShema = Depends(get_admin),
):
    email = body.email.lower()
    _status = body.status
    user = await db.scalar(
        select(User)
        .options(selectinload(User.stores), selectinload(User.sessions))
        .where(func.lower(User.email) == email)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.status = _status
    if _status == STATUS.ACTIVE:
        for store in user.stores:
            if store.status == STORE_STATUS.DEACTIVATED:
                store.status = STORE_STATUS.ACTIVE
    else:
        user.sessions.clear()
        await redis.delete(f"user:{user.id}")
        for store in user.stores:
            if store.status == STORE_STATUS.ACTIVE:
                store.status = STORE_STATUS.DEACTIVATED
                await redis.delete(f"store:{user.id}:{store.slug}")
    return {"success": True}


@router.post("/update-role")
async def update_role(
    body: RoleIn,
    db: AsyncSession = Depends(get_db),
    admin: UserShema = Depends(get_superadmin),
):
    email = body.email.lower()
    role = body.role

    user = await db.scalar(select(User).where(func.lower(User.email) == email))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    if user.role == role:
        return {"success": True}

    if user.role == ROLE.SUPERADMIN and role != ROLE.SUPERADMIN:
        other_superadmin = (await db.scalars(
            select(User).where(
                user.role == ROLE.SUPERADMIN, func.lower(user.email) != email
            )
        )).one_or_none()
        if not other_superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove last superadmin"
            )
    user.role = role

    return {"success": True}
