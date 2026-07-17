from typing import Optional
from libs.state_city import state_city
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime

class ROLE(Enum):
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"
    USER = "USER"
    SELLER = "SELLER"

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
