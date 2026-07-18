from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from schemas.store.entity import STORE_STATUS
from schemas.store.entity import BaseStoreSchemaOut 
from schemas.user import UserShema

class MiniStoreOut(BaseStoreSchemaOut):
    pass

class StoreOut(BaseStoreSchemaOut):
    user: UserShema

class StatusUpdate(BaseModel):
    slug: str
    status: STORE_STATUS
