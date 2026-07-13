from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class ROLE(Enum):
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"
    USER = "USER"

class STATUS(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    HIBERNATING = "hibernating"

class UserShema(BaseModel):
    id: int
    email: EmailStr
    fullname: str
    status: STATUS = STATUS.ACTIVE
    email_verified: bool = False
    role: ROLE = ROLE.USER

class RegisterSchema(BaseModel):
    fullname: str = Field(description="User fullname", min_length=3)
    email: EmailStr = Field(description="Email address")
    password: str = Field(min_length=6, description="Password (min-length: 6)")

class LoginSchema(BaseModel):
    email: EmailStr = Field(description="Email address")
    password: str = Field(min_length=6, description="Password (min-length: 6)")
