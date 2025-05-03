from pydantic import BaseModel
from typing import List
from ..models.bunq import Alias


class Avatar(BaseModel):
    uuid: str
    anchor_uuid: str
    image: List[int]
    style: str
class Profile(BaseModel):
    
class MonetaryAccount(BaseModel):
    id: int
    created: str
    updated: str
    avatar: Avatar
    overdraft_limit: float
    balance: float
    alias: Alias
    public_uuid: str
    user_id: int
    profile: Profile
    all_auto_save_id: List[int]
