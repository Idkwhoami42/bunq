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

context_lists = []

BUNQ_API1 = "42f74cf80fabb91e21fb9bde3447f793c28262048424dc4b2e58451b1d76f099"
token1 = "148a069b2de55e951993d1dd215762dda3e502053be4900bd6a20910f5b130e2" 
uid1 = "1880448"
# for 1883014 (100,000 euro)
BUNQ_API2 = "19b1837755833b1a9928c4f3e9279d265f46e7908c413d37708798ca59525f4d"
token2 = "7903aa301c90bff9d6a1a8a614d11f47e552ba1539a9be286bdeb4bd61d8d673"
uid2 = "1880450"

BUNQ_API3 = "sandbox_1ef4922132343f0676fce4bb699b145335bc58bc3fa1b3ab05cbbadf"
token3 = "a8ded8ef649300ebc394192fbc30d02e083e9328edb96b058fe0abe5662751f4" 
uid3 = "1883014"

BUNQ_API4 = "0c9a9b0820ddb79beb4350618161e0d4fa9856d091846da2d1221ece5708860f"
token4 = "8142df8932f89637a4a03b608c90abdbfb4aa4fff1c8ba55e653ffbd306504c6" 
uid4 = "1883014"


uid_to_context = {uid1: (BUNQ_API1, token1), uid2: (BUNQ_API2, token2), uid3: (BUNQ_API3, token3), uid4: (BUNQ_API4, token4)}
name_to_uid = {"C. Mason": uid1, "A. Mason": uid2, "C. Rogers": uid3, "T. Fisher": uid4}
BUNQ_API = BUNQ_API1
token = token1


if os.path.exists("bunq_api_context1.conf"):
    os.remove("bunq_api_context1.conf")
    
api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, BUNQ_API, "Hackathon")
api_context.save("bunq_api_context1.conf")


# Load the API context into the SDK
BunqContext.load_api_context(api_context)

user_context = BunqContext.user_context()

def change_context(user_id: str):
    if user_id in uid_to_context:
        api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, uid_to_context[user_id][0], "Hackathon")
        BunqContext.load_api_context(api_context)
        user_context = BunqContext.user_context()
    else:
        raise ValueError("User not found")



@app.get("/user-person/{itemId}", operation_id="get_user_person")
def user_person(itemId: str):
    """Get the user person for the given itemId

    Args:
        itemId (str): The itemId of the user person

    Returns:
        dict: The user person for the given itemId
    """
    change_context(itemId)
    token = uid_to_context[itemId][1]
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
    change_context(userId)
    token = uid_to_context[userId][1]
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
    change_context(userId)
    token = uid_to_context[userId][1]
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
    change_context(userId)
    token = uid_to_context[userId][1]
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
    change_context(userId)
    token = uid_to_context[userId][1]   
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

#add an account to the user
@app.post("/user/{userID}/monetary-account-bank", operation_id="add_monetary_account_to_user")
def add_monetary_account_to_user(userID: int):
    """Add a monetary account to the given userID

    Args:
        userID (str): The userId of the user
    """
    change_context(userID)
    token = uid_to_context[userID][1]
    response = requests.post(
        f"https://public-api.sandbox.bunq.com/v1/user/{userID}/monetary-account-bank",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
        data= json.dumps({"currency": "EUR"}),
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
    change_context(userId)
    token = uid_to_context[userId][1]
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId}/monetary-account/{monetaryAccountId}/request-inquiry",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

#pay money between users
@app.post("/user/{userId}/monetary-account/{monetaryAccountId}/payment", operation_id="pay_money_between_users")
def pay_money_between_users(userId1: str, monetaryAccountId1: str, userId2: str, monetaryAccountId2: str, amount: float):
    """Pay money between users

    Args:
        userId1 (str): The userId of the user getting money
        monetaryAccountId1 (str): The monetaryAccountId of the user
        userId2 (str): The userId of the user sending money
        monetaryAccountId2 (str): The monetaryAccountId of the user sending money
        amount (float): The amount of money to pay
    """
    change_context(userId1)
    token = uid_to_context[userId1][1]
    response1 = requests.post(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId1}/monetary-account/{monetaryAccountId1}/payment",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
        data= json.dumps({"amount": amount}),
        timeout=1000
    )
    change_context(userId2)
    token = uid_to_context[userId2][1]
    response2 = requests.post(
        f"https://public-api.sandbox.bunq.com/v1/user/{userId2}/monetary-account/{monetaryAccountId2}/payment",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
        data= json.dumps({"amount": amount}),
        timeout=1000
    )
    data1 = response1.json()
    data2 = response2.json()
    return data1, data2
    

mcp = FastApiMCP(app)

@app.on_event("startup")
def startup_event():
    mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)