import json
import os
from fastapi import APIRouter
import mcp
import requests
from dotenv import load_dotenv
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType

load_dotenv()

router = APIRouter(
    prefix="/bunq",
)
users = {
    "C. Mason": {
        "uid": "1880448",
        "api_key": "42f74cf80fabb91e21fb9bde3447f793c28262048424dc4b2e58451b1d76f099",
        "token": "148a069b2de55e951993d1dd215762dda3e502053be4900bd6a20910f5b130e2"
    },
    "A. Underwood": {
        "uid": "1880450",
        "api_key": "19b1837755833b1a9928c4f3e9279d265f46e7908c413d37708798ca59525f4d",
        "token": "7903aa301c90bff9d6a1a8a614d11f47e552ba1539a9be286bdeb4bd61d8d673"
    },
    "C. Rogers": {
        "uid": "1883014",  # (100,000 euro)
        "api_key": "sandbox_1ef4922132343f0676fce4bb699b145335bc58bc3fa1b3ab05cbbadf",
        "token": "a8ded8ef649300ebc394192fbc30d02e083e9328edb96b058fe0abe5662751f4"
    },
    "T. Fisher": {
        "uid": "1880451",
        "api_key": "0c9a9b0820ddb79beb4350618161e0d4fa9856d091846da2d1221ece5708860f",
        "token": "8142df8932f89637a4a03b608c90abdbfb4aa4fff1c8ba55e653ffbd306504c6"
    }
}

def change_context(name: str):
    global user_context
    global api_context
    if name in users:
        user = users[name]
        API_KEY = user["api_key"]

        if  os.path.exists("context.conf"):
            os.remove("context.conf")
            print("bunq_api_context.conf removed")
        else:
            print("bunq_api_context.conf does not exist")

        api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, API_KEY, "Hackathon")
        api_context.save("context.conf")
        print("api_context created")
        BunqContext.load_api_context(api_context)
        print("api_context loaded")
        user_context = BunqContext.user_context()
        print("user_context loaded")
    else:
        raise ValueError("User not found")



# @router.get("/user-person/{name}", operation_id="get_user_person")
def get_user_details(name: str):
    """Get the user person for the given name

    Args:
        name (str): The name of the user person

    Returns:
        dict: The user person for the given name
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user-person/{user_id}",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

# @router.get("/user/{name}/monetary-account-bank", operation_id="get_monetary_account_bank")
def get_user_monetary_account_bank(name: str):
    """Get the monetary account bank for the given name

    Args:
        name (str): The name of the user
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account-bank",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

# @router.get("/user/{name}/monetary-account/{monetaryAccountId}/payment", operation_id="get_payment_from_monetary_account")
def get_payment_from_user_account(name: str, monetaryAccountId: str):
    """Get the payment for the given name and monetaryAccountId

    Args:
        name (str): The name of the user
        monetaryAccountId (str): The monetaryAccountId of the user
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account/{monetaryAccountId}/payment",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

# @router.get("/user/{name}/event", operation_id="get_event_user")
def get_user_event_details(name: str):
    """Get the event for the given name

    Args:
        name (str): The name of the user
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/event",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

# @router.post("/user/{name}/card-credit", operation_id="create_card_credit_user")
def generate_credit_card_user(name: str):
    """Get the card for the given name

    Args:
        name (str): The name of the user
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]   
    response = requests.post(
       f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/card-credit",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"routerlication/json"},
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

# @router.post("/user/{name}/monetary-account-bank", operation_id="add_monetary_account_to_user")
def create_user_monetary_account(name: str):
    """Add a monetary account to the given name

    Args:
        name (str): The name of the user
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]
    response = requests.post(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account-bank",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"routerlication/json"},
        data= json.dumps({"currency": "EUR"}),
        timeout=1000
    )

    data = response.json()
    return data

# @router.post("/user/{name}/monetary-account/{monetaryAccountId}/payment", operation_id="add_money_to_account")
def deposit_funds_to_account_of_user(name: str, monetaryAccountId: str):
    """Add money to the given name and monetaryAccountId

    Args:
        name (str): The name of the user
        monetaryAccountId (str): The monetaryAccountId of the user
    """
    change_context(name)
    user_id = users[name]["uid"]
    token = users[name]["token"]
    response = requests.get(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account/{monetaryAccountId}/request-inquiry",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
        timeout=1000
    )

    data = response.json()
    return data

# @router.post("/user/{name}/monetary-account/{monetaryAccountId}/payment", operation_id="pay_money_between_users")
def pay_money_between_users(name1: str, monetaryAccountId1: str, name2: str, monetaryAccountId2: str, amount: float):
    """Pay money between users

    Args:
        name1 (str): The name of the user getting money
        monetaryAccountId1 (str): The monetaryAccountId of the user
        name2 (str): The name of the user sending money
        monetaryAccountId2 (str): The monetaryAccountId of the user sending money
        amount (float): The amount of money to pay
    """
    print("pay_money_between_users")
    print(name1)
    change_context(name1)
    print("context changed")
    
    user_id1 = users[name1]["uid"]
    token = users[name1]["token"]
    response1 = requests.post(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id1}/monetary-account/{monetaryAccountId1}/payment",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"routerlication/json"},
        data= json.dumps({"amount": amount}),
        timeout=1000
    )

    change_context(name2)
    user_id2 = users[name2]["uid"]
    token = users[name2]["token"]
    response2 = requests.post(
        f"https://public-api.sandbox.bunq.com/v1/user/{user_id2}/monetary-account/{monetaryAccountId2}/payment",
        headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"routerlication/json"},
        data= json.dumps({"amount": amount}),
        timeout=1000
    )
    data1 = response1.json()
    data2 = response2.json()
    return data1, data2


all_functions = [
    get_user_details,
    get_user_monetary_account_bank,
    get_payment_from_user_account,
    get_user_event_details,
    # generate_credit_card_user,
    # create_user_monetary_account,
    # deposit_funds_to_account_of_user,
    # pay_money_between_users
]

# if __name__ == "__main__":
#     # Example usage
#     name = "C. Mason"

#     print(get_user_details(name))