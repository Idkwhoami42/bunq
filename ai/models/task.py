from pydantic import BaseModel
from typing import List

class Goal(BaseModel):
    description: str
    amount: float

class Pot(BaseModel):
    description: str
    goals: List[Goal]
