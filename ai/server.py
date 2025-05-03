from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.misc import ChatRequest, ConversationState, State, Message
from models.task import ChatResponse, Pot
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from utils.prompts import get_prompt, prompt_to_determine_state
from typing import List, Dict
import uvicorn

load_dotenv()

# initialize gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

model_name = "gemini-2.0-flash"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Track conversation state 
conversation_states: Dict[str, ConversationState] = {}

@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat requests and return AI-generated responses."""
    
    if request.conversation_id not in conversation_states:
        conversation_states[request.conversation_id] = ConversationState(state=State.PRE_POT_CREATION)

    state_pv = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ConversationState,
            system_instruction=prompt_to_determine_state(request)
        )
    )
    
    if state_pv.parsed:
        conversation_states[request.conversation_id] = state_pv.parsed
    else:
        raise HTTPException(status_code=400, detail="Failed to parse conversation state")
    
    conversation_state = conversation_states[request.conversation_id].state
    
    print("The current conversation state is: ", conversation_state)
    
    if conversation_state == State.PRE_POT_CREATION:
        return pre_pot_creation(request)
    
    if conversation_state == State.POT_CAN_BE_CREATED:
        return pot_can_be_created(request)
        
    if conversation_state == State.POT_CREATED:
        return pot_created(request)
    
    if conversation_state == State.EVENT_STARTED:
        return event_started(request)
    
    raise HTTPException(status_code=400, detail="Invalid state")


def extract_pot(messages: List[Message]):
    """Extract the pot from the messages"""
    
    pot_pv = client.models.generate_content(
        model=model_name,
        contents=str(messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Pot,
            system_instruction="Extract the pot from the messages"
        )
    )
    
    if pot_pv.parsed:
        return pot_pv.parsed
    else:
        raise HTTPException(status_code=400, detail="Failed to parse pot")
    
def modify_pot(pot: Pot, messages: List[Message]):
    """Modify the pot based on the messages"""
    pot_pv = client.models.generate_content(
        model=model_name,
        contents=str(messages) + "\n\nThe current pot is: " + str(pot),
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=Pot, system_instruction="Modify the pot based on the messages")
    )

    if pot_pv.parsed:
        return pot_pv.parsed
    else:
        raise HTTPException(status_code=400, detail="Failed to parse pot")

def pre_pot_creation(request: ChatRequest):
    """Handle pre-pot creation requests"""
    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=get_prompt(request.participants, request.pot, State.PRE_POT_CREATION)
        )
    )
    
    print(response.text)
    
    return ChatResponse(message=response.text)

def pot_can_be_created(request: ChatRequest):
    """Handle pot can be created requests"""
    pot = extract_pot(request.messages)
    conversation_states[request.conversation_id].state = State.POT_CREATED
    return ChatResponse(message="Here is the shared pot that we have created for you!", pot=pot)

def pot_created(request: ChatRequest):
    """Handle pot created requests"""
    pot = modify_pot(request.pot, request.messages)
    
    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages) + "\n\nThe original pot was: " + str(request.pot) + "\n\nThe modified pot is: " + str(pot),
        config=types.GenerateContentConfig(
            system_instruction=get_prompt(request.participants, pot, State.POT_CREATED)
        )
    )
    
    return ChatResponse(message=response.text, pot=pot)

def event_started(request: ChatRequest):
    """Handle post-event requests"""
    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=get_prompt(request.participants, request.pot, State.EVENT_STARTED)
        )
    )
    
    return ChatResponse(message=response.text, pot=request.pot)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)