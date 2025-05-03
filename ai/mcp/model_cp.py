from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import os
from dotenv import load_dotenv
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
import requests
import json
import uvicorn

load_dotenv()

app = FastAPI()


BUNQ_API = "sandbox_1ef4922132343f0676fce4bb699b145335bc58bc3fa1b3ab05cbbadf"
token = "a8ded8ef649300ebc394192fbc30d02e083e9328edb96b058fe0abe5662751f4" 
# for 1883014 (100,000 euro)


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

@app.on_event("startup")
def startup_event():
    mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)