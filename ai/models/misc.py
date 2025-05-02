from pydantic import BaseModel
from typing import List
from enum import Enum

class Message(BaseModel):
    role: str
    content: str
    
class Location(BaseModel):
    latitude: float
    longitude: float

class ChatRequest(BaseModel):
    conversation_id: str
    location: Location
    messages: List[Message]
    
class State(str, Enum):
    CREATING_POT = "creating_pot"
    POT_CREATED = "pot_created"
    POST_EVENT = "post_event"

class ConversationState(BaseModel):
    state: State
