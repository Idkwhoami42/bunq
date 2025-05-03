from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from models.task import Pot

class Message(BaseModel):
    role: str
    content: str
    
class Location(BaseModel):
    latitude: float
    longitude: float

class ChatRequest(BaseModel):
    conversation_id: str
    participants: List[str]
    location: Location
    messages: List[Message]
    pot: Optional[Pot] = None
    
class State(str, Enum):
    PRE_POT_CREATION = "pre_pot_creation"
    POT_CAN_BE_CREATED = "pot_can_be_created"
    POT_CREATED = "pot_created"
    EVENT_STARTED = "event_started"

class ConversationState(BaseModel):
    state: State
