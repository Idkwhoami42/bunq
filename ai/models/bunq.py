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

class Alias(BaseModel):
    type: str
    value: str
    name: str

class MonetaryAccount(BaseModel):
    currency: str
    description: str
    daily_limit: MonetaryValue
    balance: MonetaryValue
    owner_name: str
    alias: Alias

class Payment(BaseModel):
    sender_name: str
    counterparty_name: str
    location: Location
    amount: MonetaryValue
    description: str





    
    
