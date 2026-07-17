from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.db import get_db
from models.db import get_db
from models.user import User, Session, Store
from schemas.user import UserShema, STATUS, ROLE, SessionUserSchema
from schemas.store.entity import STORE_STATUS, BaseStoreSchemaOut, StoreSchema
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .jwt import decode
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from .redis import redis

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/signin")


async def get_user(
    db: AsyncSession = Depends(get_db), token: Optional[str] = Depends(oauth2)
) -> UserShema:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )
    data = decode(token)
    session_id = data["session_id"]

    session_raw = await redis.get(f"session:{session_id}")
    session = None

    now = datetime.now(timezone.utc)

    if session_raw:
        session = SessionUserSchema.model_validate_json(session_raw)
    else:
        s = await db.scalar(
            select(Session)
            .options(selectinload(Session.user))
            .where(Session.id == session_id, Session.expired_at > now)
        )

        if not s:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired session",
            )

        session = SessionUserSchema.model_validate(s)

        json_session = session.model_dump_json()
        time_left = session.expired_at - now
        seconds_left = int(time_left.total_seconds())
        if seconds_left > 0:
            await redis.set(f"session:{session.id}", json_session, ex=seconds_left)

    user = session.user

    if user.status != STATUS.ACTIVE:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account"
        )

    return user


async def get_store(
    store_id: str,
    user: UserShema = Depends(get_user), db: AsyncSession = Depends(get_db)
) -> StoreSchema:

    if user.role != ROLE.SELLER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised Access"
        )
    
    slug = store_id.lower().strip()
    redis_res = await redis.get(f"store:{user.id}:{slug}")

    if redis_res:
        return StoreSchema.model_validate_json(redis_res)

    store = await db.scalar(
        select(Store)
        .where(Store.user_id == user.id, Store.slug == slug)
    )

    if not store:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Store does not exist in our system.",
        )

    if store.status != STORE_STATUS.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This store is {store.status}, contact support for more info",
        )

    store_dict = BaseStoreSchemaOut.model_validate(store).model_dump()
    store_dict['user'] = user
    final_store = StoreSchema.model_validate(store_dict)

    await redis.set(f"store:{user.id}:{slug}", final_store.model_dump_json(), ex=3600)
    return final_store


async def get_admin(user: UserShema = Depends(get_user)) -> UserShema:
    if user.role != ROLE.ADMIN and user.role != ROLE.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unathorised Access"
        )
    return user


async def get_superadmin(user: UserShema = Depends(get_user)) -> UserShema:
    if user.role != ROLE.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unathorised Access"
        )
    return user
