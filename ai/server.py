from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.misc import ChatRequest, ConversationState, State, Message
from google import genai
from google.genai import types
import os
from models.task import Pot
from dotenv import load_dotenv
from utils.prompts import FINANCIAL_PLANNER_PROMPT
from typing import List, Dict, Any
import json
import uvicorn

load_dotenv()

# initialize gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
def chat(request: ChatRequest):
    """Handle chat requests and return AI-generated responses."""
    
    conversation_id = request.conversation_id
    
    if conversation_id not in conversation_states:
        conversation_states[conversation_id] = ConversationState(state=State.CREATING_POT)

    state_pv = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ConversationState,
            system_instruction=FINANCIAL_PLANNER_PROMPT+'\n\nDetermine the state of the conversation based on the conversation history'
        )
    )
    
    if state_pv.parsed:
        conversation_states[conversation_id] = state_pv.parsed
        
    print(conversation_states[conversation_id])
    
    # If data is complete, try to extract the pot
    if conversation_states[conversation_id].state == State.POT_CREATED:
        pot = extract_pot(request.messages)
        if pot:
            conversation_states[conversation_id].state = State.POST_EVENT
            return pot
    
    # Continue the conversation
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=FINANCIAL_PLANNER_PROMPT
        )
    )
    
    print(response.text)

    return response.text

def extract_pot(messages: List[Message]):
    """Extract the pot from the messages"""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=str(messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Pot,
            system_instruction="Extract the pot from the messages"
        )
    )
    
    if response.parsed:
        return str(response.parsed)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)