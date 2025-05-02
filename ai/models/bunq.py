from pydantic import BaseModel
from typing import List, Dict

class Location(BaseModel):
    latitude: float
    longitude: float

class User(BaseModel): #Come back to this
    id: int
    name: str
    location: Location
    pot_ids: List[int]
    account_ids: List[int]


class MonetaryValue(BaseModel):
    value: float
    currency: str

class MonetaryAccount(BaseModel):
    currency: str
    description: str
    daily_limit: MonetaryValue

class Payment(BaseModel):
    amount: MonetaryValue
    description: str

class Contribution(BaseModel):
    user_id: int
    amount: MonetaryValue



class Pot(BaseModel):
    pot_id: int
    name: str
    description: str
    target_balance: MonetaryValue
    user_ids: List[int]
    individual_balance: List[Contribution]

    
    
