from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.misc import ChatRequest, ConversationState, State, Message
from models.task import (
    ChatResponse,
    Pot,
    RelevantParticipants,
    Question,
    Activities,
    Location,
)
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from utils.prompts import (
    get_prompt,
    prompt_to_determine_state,
    TRIVIA_PROMPT,
    CHECK_FINANCIAL_DECISIONS_PROMPT,
)
from utils.api_handler import get_user_accounts
from typing import List, Dict
import uvicorn
import requests
import json
from routers.bunq import all_functions

from fastapi_mcp import FastApiMCP
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
import uvicorn
from google import genai
from google.genai import types

app = FastAPI()

# for 1883014 (100,000 euro), carly rogers 
BUNQ_API = "sandbox_1ef4922132343f0676fce4bb699b145335bc58bc3fa1b3ab05cbbadf"
token = "a8ded8ef649300ebc394192fbc30d02e083e9328edb96b058fe0abe5662751f4" 
GEMINI_API = os.getenv("GEMINI_API_KEY")

# initialize gemini client
client = genai.Client(api_key=GEMINI_API)

model_name = "gemini-2.0-flash"

if os.path.exists("bunq_api_context.conf"):
    os.remove("bunq_api_context.conf")
    
api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, BUNQ_API, "Hackathon")
api_context.save("bunq_api_context.conf")


# Load the API context into the SDK
BunqContext.load_api_context(api_context)

user_context = BunqContext.user_context()

@app.get("/user-person/{itemId}", operation_id="get_user_person")
def user_person(itemId: str):
    """Get the user person for the given itemId

    Args:
        itemId (str): The itemId of the user person

    Returns:
        dict: The user person for the given itemId
    """
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user-person/{itemId}",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

@app.get("/user/{userId}/monetary-account-bank", operation_id="get_monetary_account_bank")
def monetary_account_bank(userId: str):
    """Get the monetary account bank for the given userId

    Args:
        userId (str): The userId of the user
    """
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId}/monetary-account-bank",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

@app.get("/user/{userId}/monetary-account/{monetaryAccountId}/payment", operation_id="get_payment_from_monetary_account")
def payment(userId: str, monetaryAccountId: str):
    """Get the payment for the given userId and monetaryAccountId

    Args:
        userId (str): The userId of the user
        monetaryAccountId (str): The monetaryAccountId of the user
"""
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId}/monetary-account/{monetaryAccountId}/payment",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

# https://public-api.sandbox.bunq.com/v1/user/{userID}/event
@app.get("/user/{userId}/event", operation_id="get_event_user")
def event(userId: str):
    """Get the event for the given userId

    Args:
        userId (str): The userId of the user
    """

    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId}/event",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    
    return data

# https://public-api.sandbox.bunq.com/v1/user/{userID}/card-credit
@app.post("/user/{userId}/card-credit", operation_id="create_card_credit_user")
def card_credit(userId: str):
    """Get the card for the given userId

    Args:
        userId (str): The userId of the user
    """
    response = requests.post(
       f"https://public-api.sandbox.bunq.com/v1/user/{userId}/card-credit",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
        data=json.dumps(
            {"first_line":"text",
             "second_line":"text",
             "name_on_card":"text",
             "preferred_name_on_card":"text",
             "type":"MASTERCARD",
             "product_type":"MAESTRO_DEBIT",
             "monetary_account_id_fallback":1,
             "order_status":"NEW_CARD_REQUEST_RECEIVED"
             }),
        timeout=1000
    )

    data = response.json()
    return data

# adding money to account
@app.post("/user/{userId}/monetary-account/{monetaryAccountId}/payment", operation_id="add_money_to_account")
def add_money_to_account(userId: str, monetaryAccountId: str):
    """Add money to the given userId and monetaryAccountId

    Args:
        userId (str): The userId of the user
        monetaryAccountId (str): The monetaryAccountId of the user
    """
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId}/monetary-account/{monetaryAccountId}/request-inquiry",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

mcp = FastApiMCP(app)

tools = [
    user_person,
    monetary_account_bank,
    payment,
    event,
    card_credit,
    add_money_to_account
]

if __name__ == "__main__":
    mcp.mount()
    
    response = client.models.generate_content(
    model=model_name,
    contents="What is user id 1883014's monetary accounts?",
    config=types.GenerateContentConfig(tools=tools),
    )
    

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

print(all_functions)

def extract_participants(messages: List[Message]):
    """Extract the participants from the messages"""
    participants_pv = client.models.generate_content(
        model=model_name,
        contents=str(messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RelevantParticipants,
            system_instruction="Based on the most recent user messages, choose the most relevant participants[need not be all participants]",
            # tools=all_functions,
        ),
    )
    return participants_pv.parsed


def extract_pot(messages: List[Message]):
    """Extract the pot from the messages"""

    pot_pv = client.models.generate_content(
        model=model_name,
        contents=str(messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Pot,
            system_instruction="Extract the pot from the messages",
            # tools=all_functions,
        ),
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
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Pot,
            system_instruction="Modify the pot based on the messages",
            # tools=all_functions,
        ),
    )

    if pot_pv.parsed:
        return pot_pv.parsed
    else:
        raise HTTPException(status_code=400, detail="Failed to parse pot")


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat requests and return AI-generated responses."""

    if request.conversation_id not in conversation_states:
        conversation_states[request.conversation_id] = ConversationState(
            state=State.PRE_POT_CREATION
        )

    state_pv = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ConversationState,
            system_instruction=prompt_to_determine_state(request),
            # tools=all_functions,
        ),
    )

    if state_pv.parsed:
        conversation_states[request.conversation_id] = state_pv.parsed
    else:
        raise HTTPException(
            status_code=400, detail="Failed to parse conversation state"
        )

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


def pre_pot_creation(request: ChatRequest):
    """Handle pre-pot creation requests"""

    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            # system_instruction=get_prompt(
            #     request.participants, request.pot, State.PRE_POT_CREATION, request
            # ),
            tools=[google_search_tool].extend(all_functions),
            response_modalities=["TEXT"],

        ),
    )

    return ChatResponse(message=response.text)


def pot_can_be_created(request: ChatRequest):
    """Handle pot can be created requests"""
    pot = extract_pot(request.messages)
    conversation_states[request.conversation_id].state = State.POT_CREATED
    return ChatResponse(
        message="Here is the shared pot that we have created for you!", pot=pot
    )


def pot_created(request: ChatRequest):
    """Handle pot created requests"""
    relevant_participants = extract_participants(request.messages)
    new_pot = modify_pot(request.pot, request.messages)

    prompt_task = get_prompt(relevant_participants, new_pot, State.POT_CREATED, request)

    print("The prompt task is: ", prompt_task)

    if "trivia" not in prompt_task:
        response = client.models.generate_content(
            model=model_name,
            contents=str(request.messages),
            config=types.GenerateContentConfig(system_instruction=prompt_task),
            tools=all_functions
        )
    else:
        question_pv = client.models.generate_content(
            model=model_name,
            contents=str(request.messages),
            config=types.GenerateContentConfig(
                system_instruction=prompt_task,
                response_mime_type="application/json",
                response_schema=Question,
                # tools=all_functions,
            ),
        )
        if question_pv.parsed:
            print("The question is: ", question_pv.parsed)
            return ChatResponse(
                message="Here is the trivia question for you!",
                pot=new_pot,
                question=question_pv.parsed,
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to parse question")
    return ChatResponse(message=response.text, pot=new_pot)


def event_started(request: ChatRequest):
    """Handle post-event requests"""
    # determine which function to call based on the messages
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    response = client.models.generate_content(
        model=model_name,
        contents=str(request.messages),
        config=types.GenerateContentConfig(
            system_instruction=get_prompt(
                request.participants, request.pot, State.EVENT_STARTED, request
            ),
            tools=[google_search_tool].extend(all_functions),
            response_modalities=["TEXT"],
        ),
    )

    activities, place = possible_activities(response.text)

    locations = [get_location_for_activity(activity, place) for activity in activities]

    # map locations to the Location object
    locations = [
        Location(
            name=location["displayName"]["text"],
            google_maps_uri=location["googleMapsUri"],
            website_uri=location["websiteUri"] if "websiteUri" in location else None,
            latitude=location["location"]["latitude"]
            if "location" in location
            else None,
            longitude=location["location"]["longitude"]
            if "location" in location
            else None,
        )
        for location in locations
    ]

    print("The locations are: ", locations)

    return ChatResponse(message=response.text, pot=request.pot, locations=locations)


def get_location_for_activity(activity: str, place: str):
    """Get location information for a given activity using Google Places API"""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GEMINI_API_KEY"),
        "X-Goog-FieldMask": "places.displayName,places.googleMapsUri,places.websiteUri,places.location",
    }

    data = {"textQuery": activity + " in " + place}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        # if the response is not empty, return the first location
        if response.json()["places"]:
            return response.json()["places"][0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch location data: {str(e)}"
        )


def possible_activities(response: str):
    """Get the locations from the response"""
    # find all the locations in the response
    activities_pv = client.models.generate_content(
        model=model_name,
        contents=response,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Activities,
            system_instruction="Extract the activities from the response",
        # tools=all_functions,

        ),
    )

    if activities_pv.parsed:
        return activities_pv.parsed.activities, activities_pv.parsed.place
    else:
        raise HTTPException(status_code=400, detail="Failed to parse activities")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)