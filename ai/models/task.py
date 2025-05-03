from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    JPY = "JPY"

class ParticipantAmount(BaseModel):
    participant: str
    currency: Currency
    expected_amount: float
    amount_contributed: float

class IndividualSaving(BaseModel):
    description: str
    participant_amounts: List[ParticipantAmount]

class SharedSaving(BaseModel):
    description: str
    currency: Currency
    expected_amount: float
    amount_contributed: float

class Pot(BaseModel):
    description: str
    individual_savings: List[IndividualSaving]
    shared_savings: List[SharedSaving]

class RelevantParticipants(BaseModel):
    participants: List[str]

class Option(BaseModel):
    option: str
    correct: bool

class Question(BaseModel):
    question: str
    options: List[Option]
    correct_option: str


class ChatResponse(BaseModel):
    message: str
    pot: Optional[Pot] = None
    question: Optional[Question] = None



