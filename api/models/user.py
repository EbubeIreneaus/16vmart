import uuid

from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, Integer, String, Boolean, ForeignKey, DateTime, Enum
from pydantic import EmailStr, HttpUrl
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlalchemy.sql import func
from schemas.user import ROLE, STATUS
from schemas.store.entity import STORE_STATUS

if TYPE_CHECKING:
    from .product import Product
    from .shopping import Order, Wishlist


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[EmailStr] = mapped_column(String(40), unique=True, nullable=False)
    email_verified: Mapped[Boolean] = mapped_column(Boolean, default=False)
    role: Mapped[ROLE] = mapped_column(Enum(ROLE), default=ROLE.USER)
    status: Mapped[STATUS] = mapped_column(Enum(STATUS), default=STATUS.ACTIVE)
    password: Mapped[str] = mapped_column(String, nullable=True)
    orders: Mapped[List[Order]] = relationship(back_populates="user")
    wishlists: Mapped[List[Wishlist]] = relationship(back_populates="user",  cascade="all, delete-orphan")  
    addresses: Mapped[List[Address]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[List["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    stores: Mapped[List[Store]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class Address(Base):
    __tablename__="addresses"
    id: Mapped[int] = mapped_column(primary_key=True)

    address_id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4(), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="addresses")
    state: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    landmark: Mapped[str]=mapped_column(String, nullable=True)
    zip_code: Mapped[int] = mapped_column(Integer)
    line_1:Mapped[str] = mapped_column(String)
    line_2: Mapped[str] = mapped_column(String, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[User] = relationship(back_populates="sessions")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    device: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_address: Mapped[str] = mapped_column(String)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    refresh_token_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Store(Base):
    __tablename__ = "stores"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[Optional[User]] = relationship(back_populates="stores")
    logo: Mapped[Optional[HttpUrl]] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(18))
    state: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String)
    industry: Mapped[str] = mapped_column(String)
    email: Mapped[EmailStr] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[STORE_STATUS] = mapped_column(Enum(STORE_STATUS), default=STORE_STATUS.ACTIVE)
    products: Mapped[List[Product]] = relationship(back_populates="store", cascade="all, delete-orphan")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
