from .db import Base
from sqlalchemy import (
    JSON,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    Enum,
    Boolean,
    Float,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Literal, Optional, TYPE_CHECKING
from decimal import Decimal
from schemas.product import CONDITION, FormTypeLiteral
from datetime import datetime
from pydantic import HttpUrl



if TYPE_CHECKING:
    from .user import Store

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=11, scale=2), default=Decimal("0.0"))
    description: Mapped[str] = mapped_column(String, nullable=False)
    condition: Mapped[CONDITION] = mapped_column(Enum(CONDITION), default=CONDITION.NEW)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped[Category] = relationship(back_populates="products")
    attributes: Mapped[List[ProductAttribute]] = relationship(back_populates="product", cascade="all, delete-orphan")
    store: Mapped[Store] = relationship(back_populates="products")
    store_id: Mapped[int] = mapped_column(ForeignKey('stores.id'))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_update: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )
    images: Mapped[List[ProductImages]] = relationship(back_populates="product", cascade="all, delete-orphan")
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)


class ProductImages(Base):
    __tablename__ = "product_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True) #user as cloudinary public id
    src: Mapped[HttpUrl] = mapped_column(Text, nullable=False)
    alt: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    product_id: Mapped[int] =  mapped_column(ForeignKey('products.id'))
    product: Mapped[Product] = relationship(back_populates="images")

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    parent: Mapped[Optional[Category]] = relationship(
        back_populates="sub_categories", remote_side=[id]
    )

    sub_categories: Mapped[List[Category]] = relationship(back_populates="parent")
    products: Mapped[List[Product]] = relationship(back_populates="category")
    attributes: Mapped[List[AttributeKey]] = relationship(back_populates="category")


class AttributeKey(Base):
    __tablename__ = "attribute_keys"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    form_type: Mapped[FormTypeLiteral] = (
        mapped_column(String(25), default="text")
    )
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped[Category] = relationship(
        back_populates="attributes"
    )
    attributes: Mapped[List[ProductAttribute]] = relationship(
        back_populates="attribute",
    )


class ProductAttribute(Base):
    __tablename__ = "product_attributes"
    id: Mapped[int] = mapped_column(primary_key=True)
    attribute_id: Mapped[int] = mapped_column(ForeignKey("attribute_keys.id"))
    attribute: Mapped[AttributeKey] = relationship(back_populates="attributes")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped[Product] = relationship(
        back_populates="attributes"
    )

    json_value: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    text_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    date_value: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    number_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    boolean_value: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    __table_args__ = (
        UniqueConstraint("product_id", "attribute_id", name="uq_product_attribute"),
    )
