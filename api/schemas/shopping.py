from datetime import datetime
from decimal import Decimal
from schemas.product import MiniProductResponse
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from enum import Enum
from typing import Any, Optional, List, Literal
import uuid
from schemas.user import AddressOutschema

class ORDER_STATUS(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"

class WishlistIn(BaseModel):
    product_id: str #slug

class WishlistOut(BaseModel):
    product: MiniProductResponse
    created_at: datetime

class BaseOrderMini(BaseModel):
    order_number: str
    idompotent_key: uuid.UUID
    status: ORDER_STATUS
    paid_at: Optional[datetime]
    paid: bool
    created_at: datetime

class OrderProduct(BaseModel):
    product: MiniProductResponse
    quantity: int = 1

class SingleOrderOut(BaseOrderMini):
    delivery_address: AddressOutschema
    items: List[OrderProduct]

