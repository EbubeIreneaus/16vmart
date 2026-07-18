from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from enum import Enum
from typing import Any, Optional, List, Literal
from schemas.admin.product import AttributeKeySchema

class CategorySchema(BaseModel):
    id: int
    slug: str
    name: str

class CategoryResp(CategorySchema):
    sub_categories: List[CategorySchema]

class AttrRsp(AttributeKeySchema):
    pass