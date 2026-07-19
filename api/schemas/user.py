from typing import Optional
from libs.state_city import state_city
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
import uuid

class ROLE(Enum):
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    USER = "user"
    SELLER = "seller"

class STATUS(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    HIBERNATING = "hibernating"
    UNDER_REVIEW = "under_review"

class UserShema(BaseModel):
    id: int
    email: EmailStr
    fullname: str
    status: STATUS = STATUS.ACTIVE
    email_verified: bool = False
    role: ROLE = ROLE.USER

    model_config = ConfigDict(from_attributes=True)

class SessionSchema(BaseModel):
    id: int
    location: Optional[str] = None
    ip_address: Optional[str] = None
    device: Optional[str] = None
    expired_at: datetime
    created_at: datetime

class SessionUserSchema(SessionSchema):
    user: UserShema
    
    model_config = ConfigDict(from_attributes=True)
    

class RegisterSchema(BaseModel):
    fullname: str = Field(description="User fullname", min_length=3)
    email: EmailStr = Field(description="Email address")
    password: str = Field(min_length=6, description="Password (min-length: 6)")

    model_config = ConfigDict(extra="forbid")

class LoginSchema(BaseModel):
    email: EmailStr = Field(description="Email address")
    password: str = Field(min_length=6, description="Password (min-length: 6)")

class BaseAddress(BaseModel):
    state: str
    city: str
    landmark: Optional[str] = None
    line_1: str
    line_2: Optional[str] = None
    zip_code: int

class AddressInSchema(BaseAddress):
    pass
class AddressOutschema(BaseAddress):
    address_id: uuid.UUID

class AddressUpdate(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None
    landmark: Optional[str] = None
    line_1: Optional[str] = None
    line_2: Optional[str] = None
    zip_code: Optional[int] = None