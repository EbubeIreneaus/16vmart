from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import Optional, List, Literal

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
    id: int
    slug: str
 
class CategorySchemaResponse(CategorySchema):
    sub_categories: Optional[List[CategorySchema]] = Field(default=None)

