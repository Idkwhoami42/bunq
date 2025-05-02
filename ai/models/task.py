from pydantic import BaseModel
from typing import List

class Goal(BaseModel):
    description: str
    amount: float
    currency: str

class Pot(BaseModel):
    description: str
    goals: List[Goal]
