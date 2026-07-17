from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import Optional, List, Literal
from schemas.product import (
    BaseProductShema,
    BaseProductImages,
    BaseProductAttributeSchema,
    CONDITION
)


class ProductAttributes(BaseModel):
    attribute_id: int
    value: str


class ProductSchemaIn(BaseProductShema):
    category_id: int
    attributes: List[ProductAttributes]


class ProductSchemaUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    condition: Optional[CONDITION] = None
    available: Optional[bool] = None
