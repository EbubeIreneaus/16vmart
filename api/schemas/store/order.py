from datetime import datetime
from decimal import Decimal
from schemas.product import MiniProductResponse
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from enum import Enum
from typing import Any, Optional, List, Literal
import uuid
from schemas.user import AddressOutschema
from schemas.shopping import ORDER_STATUS, SingleOrderOut
from schemas.shopping import BaseOrderMini

class BaseVendorOrder(BaseModel):
    vid: uuid.UUID
    subtotal: Decimal
    status: Literal['paid', 'unpaid']
    created_at: datetime
    paid_at:Optional[datetime]=None

    model_config = ConfigDict(from_attributes=True)

class VendorOrderProduct(BaseModel):
    product_name: str
    quantity: int
    unit_price: Decimal

class SingleVendorOrder(BaseVendorOrder):
    items: List[VendorOrderProduct]