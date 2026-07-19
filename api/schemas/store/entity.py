from typing import Optional, TYPE_CHECKING
from libs.state_city import state_city
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from schemas.user import UserShema

class STORE_STATUS(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    HIBERNATING = "hibernating"
    UNDER_REVIEW = "under_review"
    DEACTIVATED = "deactivated"



class BaseStoreSchema(BaseModel):
    logo: Optional[str] = Field(default=None)
    phone: str
    name: str
    state: str
    city: str
    address: str
    industry: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class StoreSchemaIn(BaseStoreSchema):
    pass

class StoreSchemaUpdate(BaseModel):
    phone: Optional[str] = Field(default=None, max_length=15)
    state: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)

class BaseStoreSchemaOut(BaseStoreSchema):
    slug: str
    status: STORE_STATUS
    model_config = ConfigDict(from_attributes=True)

class StoreSchema(BaseStoreSchemaOut):
    id: int
    user: UserShema
    model_config = ConfigDict(from_attributes=True)
    