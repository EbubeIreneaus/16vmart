from typing import Optional, List
from libs.state_city import state_city
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from schemas.store.entity import BaseStoreSchemaOut 
from schemas.user import ROLE, UserShema, SessionSchema, STATUS

class MiniUserResp(UserShema):
    pass

class UserResp(UserShema):
    stores: Optional[List[BaseStoreSchemaOut]] = None
    sessions: Optional[List[SessionSchema]] = None

class StatusIn(BaseModel):
    email: EmailStr
    status: STATUS
class RoleIn(BaseModel):
    email: EmailStr
    role: ROLE