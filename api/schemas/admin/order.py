from datetime import datetime
from decimal import Decimal
from schemas.product import MiniProductResponse
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from enum import Enum
from typing import Any, Optional, List, Literal
import uuid
from schemas.user import AddressOutschema
from schemas.shopping import ORDER_STATUS, SingleOrderOut, BaseOrderMini
from schemas.store.entity import BaseStoreSchemaOut
from schemas.store.order import BaseVendorOrder
from schemas.user import UserShema

class AdminSingleOrderOut(SingleOrderOut):
    vendors: List[MiniVendorOrder]
    user: UserShema

class UpdateOrderSchema(BaseModel):
    status: ORDER_STATUS

class VendorOrderUpdate(BaseModel):
    status: Literal['paid', 'unpaid']

class MiniVendorOrder(BaseVendorOrder):
    store: BaseStoreSchemaOut

class SingleVendorOrder(MiniVendorOrder):
    order: BaseOrderMini