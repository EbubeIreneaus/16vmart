from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from enum import Enum
from typing import Any, Optional, List, Literal
from schemas.admin.product import AttributeKeySchema
from schemas.product import (
    BaseProductShema,
    BaseProductImages,
    BaseProductAttributeSchema,
    CONDITION,
    MiniProductResponse,
)


class ProductAttributesIn(BaseModel):
    attribute_id: int
    value: Any


class ProductSchemaIn(BaseProductShema):
    category_id: int
    attributes: List[ProductAttributesIn]


class ProductSchemaUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    condition: Optional[CONDITION] = None
    available: Optional[bool] = None


class MiniProductOut(MiniProductResponse):
    
    model_config = ConfigDict(from_attributes=True)


class ProductAttributeOut(BaseModel):
    name: str
    value: str | int | float | bool | list | datetime
    type: Literal["text", "date", "boolean", "number", "list"]

    model_config = ConfigDict(from_attributes=True)


class SingleProductOut(MiniProductOut):
    attributes: List[ProductAttributeOut]
    model_config = ConfigDict(from_attributes=True)
