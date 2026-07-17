from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    status,
    Response,
    Depends,
    Header,
    Cookie,
)
from fastapi.security import OAuth2PasswordBearer
from libs.jwt import encode, decode
from libs.redis import redis
from pwdlib import PasswordHash
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import RegisterSchema, LoginSchema, STATUS, SessionUserSchema
from models.user import User as UserModel, Session as SessionModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Annotated
from bg_task.config import get_arq_pool
from libs.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXP = 6000
REFRESH_TOKEN_EXP = 30

password_hash = PasswordHash.recommended()


@router.post("/signup")
@limiter.limit("25/hour", error_message="Too many request, try again later")
async def signup(
    request: Request,
    response: Response,
    body: RegisterSchema,
    session: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    try:
        email = body.email.lower()
        email_exist_stmt = await session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        if email_exist_stmt:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exist"
            )
        hashed_password = password_hash.hash(body.password)
        refresh_token = secrets.token_urlsafe(30)
        r_token_hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
        access_token_expired_at = datetime.now(timezone.utc) + timedelta(
            seconds=ACCESS_TOKEN_EXP
        )
        refresh_token_expired_at = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXP
        )

        new_user = UserModel(
            **body.model_dump(exclude={"password", "email"}),
            email=email,
            password=hashed_password,
        )
        client_ip = x_forwarded_for if x_forwarded_for else request.client.host

        new_session = SessionModel(
            user=new_user,
            refresh_token_hash=r_token_hashed,
            expired_at=refresh_token_expired_at,
            ip_address=client_ip,
        )

        session.add_all([new_user, new_session])
        await session.flush()

        jwt_encoded_data = {
            "sub": str(new_user.id),
            "session_id": new_session.id,
            "exp": access_token_expired_at,
        }
        token = encode(jwt_encoded_data)
        response.set_cookie(
            "access_token",
            token,
            expires=access_token_expired_at,
            samesite="lax",
            secure=True,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            expires=refresh_token_expired_at,
            httponly=True,
            samesite="lax",
            secure=True,
        )

        try:
            session_json = SessionUserSchema.model_validate(
                new_session
            ).model_dump_json()
            await redis.set(f"session:{session.id}", session_json, ex=ACCESS_TOKEN_EXP)
        except:
            pass

        arq = await get_arq_pool()
        await arq.enqueue_job("update_session", new_session.id, user_agent)
        await arq.enqueue_job("send_welcome_email", email, body.fullname)
        return {"success": True}

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, Try again later",
        )


@router.post("/signin")
@limiter.limit("30/hour", error_message="Too many request, try again later")
async def signin(
    request: Request,
    response: Response,
    body: LoginSchema,
    db: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    try:
        email = body.email.lower()
        fake_pass = password_hash.hash("fake password")

        stmt = select(UserModel).where(UserModel.email == email)
        user = await db.scalar(stmt)
        hashed_password = user.password if user else fake_pass
        verify_password = password_hash.verify(body.password, hashed_password)
        # verify both same time to prevent timing attack
        if not user or not verify_password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.status == STATUS.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is suspended, contact support for more details",
            )

        if user.status == STATUS.TERMINATED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is terminated and can't be accessed again.",
            )

        if user.status == STATUS.UNDER_REVIEW:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is under review, we will notify you once our descision has been made",
            )

        ip = x_forwarded_for if x_forwarded_for else request.client.host
        refresh_token = secrets.token_urlsafe(30)
        refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        access_token_expired_at = datetime.now(timezone.utc) + timedelta(
            seconds=ACCESS_TOKEN_EXP
        )
        refresh_token_expired_at = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXP
        )

        session = SessionModel(
            user=user,
            ip_address=ip,
            refresh_token_hash=refresh_hash,
            expired_at=refresh_token_expired_at,
        )

        db.add(session)
        await db.flush()

        jwt_data = {
            "sub": str(user.id),
            "session_id": session.id,
            "exp": access_token_expired_at,
        }

        token = encode(jwt_data)
        response.set_cookie(
            "access_token",
            token,
            expires=access_token_expired_at,
            samesite="lax",
            secure=True,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            expires=refresh_token_expired_at,
            httponly=True,
            samesite="lax",
            secure=True,
        )

        try:
            session_json = SessionUserSchema.model_validate(session).model_dump_json()
            await redis.set(f"session:{session.id}", session_json, ex=ACCESS_TOKEN_EXP)
        except:
            pass

        arq = await get_arq_pool()
        await arq.enqueue_job("update_session", session.id, user_agent)
        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, Try again later",
        )


@router.post("/refresh-token")
@limiter.limit("50/hour", error_message="Too many request, try again later")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid request"
        )
    hashed_refresh_token = hashlib.sha256(refresh_token.encode()).hexdigest()
    stmt = select(SessionModel).options(selectinload(SessionModel.user)).where(
        SessionModel.refresh_token_hash == hashed_refresh_token
    )
    session = await db.scalar(stmt)

    now = datetime.now(timezone.utc)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="session not found"
        )
    expire_at = session.expired_at
    if now >= expire_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="session Expired"
        )
    user_id = session.user_id
    new_refresh_token = secrets.token_urlsafe(30)
    n_r_hashed = hashlib.sha256(new_refresh_token.encode()).hexdigest()

    access_token_expire_at = datetime.now(timezone.utc) + timedelta(
        seconds=ACCESS_TOKEN_EXP
    )
    refresh_token_exp_at = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXP
    )

    session.refresh_token_hash = n_r_hashed
    session.expired_at = refresh_token_exp_at

    jwt_data = {
        "sub": str(user_id),
        "session_id": session.id,
        "exp": access_token_expire_at,
    }

    token = encode(jwt_data)

    response.set_cookie(
        "access_token",
        token,
        expires=access_token_expire_at,
        samesite="lax",
        secure=True,
    )
    response.set_cookie(
        "refresh_token",
        new_refresh_token,
        expires=refresh_token_exp_at,
        httponly=True,
        samesite="lax",
        secure=True,
    )

    try:
        session_json = SessionUserSchema.model_validate(session).model_dump_json()
        await redis.set(f"session:{session.id}", session_json, ex=ACCESS_TOKEN_EXP)
    except:
        pass

    return {"success": True}
