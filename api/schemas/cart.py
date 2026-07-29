from datetime import datetime
from decimal import Decimal
from schemas.product import MiniProductResponse
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from typing import Any, Optional, List, Literal


class CartIn(BaseModel):
    product_id: str #slug
    quantity: int = Field(default=1, ge=1)

class CartOut(BaseModel):
    product: MiniProductResponse
    quantity: int = 1
