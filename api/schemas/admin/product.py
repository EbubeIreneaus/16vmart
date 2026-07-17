from datetime import datetime
from decimal import Decimal
from schemas.product import BaseCategorySchema, CategorySchema
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import Optional, List, Literal

FormTypeLiteral = Literal["text", "select", "multiple", "radio", "date", "boolean", "number"]

class BaseAttributeKeySchema(BaseModel):
    name: str
    required: bool = Field(default=True)
    form_type: FormTypeLiteral

class AttributeKeySchema(BaseAttributeKeySchema):
    id: int

class CategorySchemaIn(BaseCategorySchema):
    attributes: Optional[List[BaseAttributeKeySchema]] = Field(default=None)
    sub_categories: Optional[List[CategorySchemaIn]] = Field(default=None)

class AdminCategorySchema(CategorySchema):
    sub_categories: List[AdminCategorySchema]
    attributes: List[AttributeKeySchema]