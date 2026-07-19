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

