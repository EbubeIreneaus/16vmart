from decimal import Decimal
import uuid

from schemas.shopping import ORDER_STATUS

from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Numeric, String, Boolean, ForeignKey, DateTime, Enum, UUID
from pydantic import EmailStr, HttpUrl
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .user import User
    from .product import Product
    from .user import Address

class Wishlist(Base):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[User] = relationship(back_populates="wishlists")
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    product: Mapped[Product] = relationship()
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class OrderProduct(Base):
    __tablename__ = "order_products"
    id: Mapped[int] = mapped_column(primary_key=True)

    product: Mapped[Product] = relationship()
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(precision=11, scale=2))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    order: Mapped[Order] = relationship(back_populates="items")
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)

    order_number: Mapped[str] = mapped_column(String, unique=True, index=True)

    user: Mapped[User] = relationship(back_populates="orders")
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    idompotent_key: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, index=True)

    items: Mapped[List[OrderProduct]] = relationship(back_populates="order", cascade="all, delete-orphan")
    deleivery_address: Mapped[Address] = relationship()
    delivery_addr_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"))
    status: Mapped[ORDER_STATUS] = mapped_column(Enum(ORDER_STATUS), default=ORDER_STATUS.PENDING)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now())
