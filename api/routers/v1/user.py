from datetime import datetime, timezone
from typing import List
import uuid

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
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from libs.deps import get_db, get_user
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import Address
from schemas.user import BaseAddress, AddressInSchema, AddressOutschema, UserShema
from libs.limiter import limiter
router = APIRouter(prefix="/user", tags=["User"])

@router.post("/create-address")
@limiter.limit("20/hour", error_message="Too many request, try again later")
async def create_address(
    request: Request,
    body: AddressInSchema,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_user),
) -> AddressOutschema:
    
    address = Address(**body.model_dump(), user_id=user.id)
    db.add(address)
    await db.flush()
    return address

@router.delete("/address/{address_id}")
async def delete_address(
    request: Request,
    address_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_user),
):
    now = datetime.now(timezone.utc)
    await db.execute(
        update(Address)
        .where(Address.address_id == address_id, Address.user_id == user.id)
        .values(deleted=True, deleted_at=now)
    )

    return {"success": True}

@router.get("/address", response_model=List[AddressOutschema])
async def get_addresses(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_user),
):
    addresses =  (await db.scalars(
        select(Address)
        .where(Address.user_id == user.id, Address.deleted_at==False)
    )).all()

    return addresses

@router.get("/address/{address_id}", response_model=List[AddressOutschema])
async def get_address(
    request: Request,
    address_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserShema = Depends(get_user),
)-> AddressOutschema:
    address =  await db.scalar(
        select(Address)
        .where(Address.user_id == user.id,Address.address_id==address_id, Address.deleted==False)
    )
    if not address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User address does not exist."
        )

    return address
