from datetime import datetime
from decimal import Decimal
from schemas.product import MiniProductResponse
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
import uuid
from typing import Any, Optional, List, Literal
from .user import AddressInSchema
from .shopping import ORDER_STATUS

class CartItem(BaseModel):
    product_id: str
    quantity: int = 1

class CheckoutIn(BaseModel):
    idompotent_key: uuid.UUID
    items: List[CartItem]
    delivery_address: uuid.UUID | AddressInSchema

class BaseOrderMini(BaseModel):
    order_number: str
    idompotent_key: uuid.UUID
    status: ORDER_STATUS
    paid_at: Optional[datetime]
    paid: bool
    created_at: datetime
