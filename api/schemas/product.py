from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from enum import Enum
from typing import Any, Optional, List, Literal


FormTypeLiteral = Literal["text", "select", "multiple", "radio", "date", "boolean", "number"]

class CONDITION(Enum):
    NEW = "brand new"
    USED = "used"

class BaseCategorySchema(BaseModel):
    name: str

class BaseProductAttributeSchema(BaseModel):
    json_value: Optional[list]
    text_value: Optional[str]
    date_value: Optional[datetime]
    number_value: Optional[float]
    boolean_value: Optional[bool]

class BaseProductShema(BaseModel):
    name: str 
    price: Decimal = Field(default=Decimal("0.0"))
    description: str
    condition: CONDITION = Field(default=CONDITION.NEW)
    available: bool = Field(default=True)

class BaseProductImages(BaseModel):
    src: HttpUrl
    alt: Optional[str] = Field(default=None)

class CategorySchema(BaseCategorySchema):
    slug: str

    model_config = ConfigDict(from_attributes=True)
 
class CategorySchemaResponse(CategorySchema):
    sub_categories: Optional[List[CategorySchema]] = Field(default=None)


class ProuctAttribute(BaseModel):
    name: str
    type: Literal["multiple","text", "number", "date", "boolean"]
    value: str|list|datetime|float|bool

class MiniProductResponse(BaseProductShema):
    slug: str
    images: List[BaseProductImages]

    model_config = ConfigDict(from_attributes=True)

class ProductResponse(MiniProductResponse):
    category: CategorySchema
    attributes: List[ProuctAttribute]
