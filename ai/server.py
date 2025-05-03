from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.misc import ChatRequest, ConversationState, State, Message
from models.task import ChatResponse, Pot, RelevantParticipants, Question
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from utils.prompts import get_prompt, prompt_to_determine_state, TRIVIA_PROMPT, CHECK_FINANCIAL_DECISIONS_PROMPT
from utils.api_handler import get_user_accounts
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
    
    # Get accounts for all participants
    # participant_accounts = {}
    # for participant in request.participants:
    #     accounts = get_user_accounts(participant)
    #     if accounts:
    #         participant_accounts[participant] = accounts
    
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

def extract_participants(messages: List[Message]):
    """Extract the participants from the messages"""
    participants_pv = client.models.generate_content(
        model=model_name,
        contents=str(messages),
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=RelevantParticipants, system_instruction="Based on the most recent user messages, choose the most relevant participants[need not be all participants]")
    )
    return participants_pv.parsed

def pre_pot_creation(request: ChatRequest):
    """Handle pre-pot creation requests"""
    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=get_prompt(request.participants, request.pot, State.PRE_POT_CREATION, request)
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
    relevant_participants = extract_participants(request.messages)
    print("The relevant participants are: ", relevant_participants)
    new_pot = modify_pot(request.pot, request.messages)
    prompt_task = get_prompt(relevant_participants, new_pot, State.POT_CREATED, request)
    if "trivia" not in prompt_task:
        response = client.models.generate_content(
            model=model_name,
            contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=prompt_task
            )
        )
    else:
        question_pv = client.models.generate_content(
            model=model_name,
            contents=str(request.messages),
            config=types.GenerateContentConfig(
                system_instruction=prompt_task,
                response_mime_type="application/json",
                response_schema=Question
            )
        )
        if question_pv.parsed:
            print("The question is: ", question_pv.parsed)
            return ChatResponse(message="Here is the trivia question for you!", pot=new_pot, question=question_pv.parsed)
        else:
            raise HTTPException(status_code=400, detail="Failed to parse question")
    return ChatResponse(message=response.text, pot=new_pot)

def event_started(request: ChatRequest):
    """Handle post-event requests"""
    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=get_prompt(request.participants, request.pot, State.EVENT_STARTED, request)
        )
    )
    
    return ChatResponse(message=response.text, pot=request.pot)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)