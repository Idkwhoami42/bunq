# from fastapi import FastAPI
# from fastapi_mcp import FastApiMCP
# import os
# from dotenv import load_dotenv
# from bunq.sdk.context.api_context import ApiContext
# from bunq.sdk.context.bunq_context import BunqContext
# from bunq import ApiEnvironmentType
# import requests
# import json
# import uvicorn

# load_dotenv()

# app = FastAPI()


# # Define users with their API keys, tokens, and UIDs
# users = {
#     "C. Mason": {
#         "uid": "1880448",
#         "api_key": "42f74cf80fabb91e21fb9bde3447f793c28262048424dc4b2e58451b1d76f099",
#         "token": "148a069b2de55e951993d1dd215762dda3e502053be4900bd6a20910f5b130e2"
#     },
#     "A. Underwood": {
#         "uid": "1880450",
#         "api_key": "19b1837755833b1a9928c4f3e9279d265f46e7908c413d37708798ca59525f4d",
#         "token": "7903aa301c90bff9d6a1a8a614d11f47e552ba1539a9be286bdeb4bd61d8d673"
#     },
#     "C. Rogers": {
#         "uid": "1883014",  # (100,000 euro)
#         "api_key": "sandbox_1ef4922132343f0676fce4bb699b145335bc58bc3fa1b3ab05cbbadf",
#         "token": "a8ded8ef649300ebc394192fbc30d02e083e9328edb96b058fe0abe5662751f4"
#     },
#     "T. Fisher": {
#         "uid": "1880451",
#         "api_key": "0c9a9b0820ddb79beb4350618161e0d4fa9856d091846da2d1221ece5708860f",
#         "token": "8142df8932f89637a4a03b608c90abdbfb4aa4fff1c8ba55e653ffbd306504c6"
#     }
# }

# # Create mappings for backwards compatibility
# name_to_uid = {name: data["uid"] for name, data in users.items()}
# uid_to_context = {data["uid"]: (data["api_key"], data["token"]) for name, data in users.items()}

# # Set default user
# BUNQ_API = users["C. Mason"]["api_key"]
# token = users["C. Mason"]["token"]
# BUNQ_API = BUNQ_API1
# token = token1


# # if os.path.exists("bunq_api_context1.conf"):
# #     os.remove("bunq_api_context1.conf")
    
# # api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, BUNQ_API, "Hackathon")
# # api_context.save("bunq_api_context1.conf")


# # Load the API context into the SDK
# # BunqContext.load_api_context(api_context)

# # user_context = BunqContext.user_context()

# def change_context(name: str):
#     global user_context
#     global api_context
#     if name in name_to_uid:
#         user_id = name_to_uid[name]
#         API_KEY = uid_to_context[user_id][0]
#         print(API_KEY)
#         print(user_id)

#         if  os.path.exists("context.conf"):
#             os.remove("context.conf")
#             print("bunq_api_context2.conf removed")
#         else:
#             print("bunq_api_context2.conf does not exist")

#         api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, API_KEY, "Hackathon")
#         api_context.save("context.conf")
#         print("api_context created")
#         BunqContext.load_api_context(api_context)
#         print("api_context loaded")
#         user_context = BunqContext.user_context()
#         print("user_context loaded")
#     else:
#         raise ValueError("User not found")



# @app.get("/user-person/{name}", operation_id="get_user_person")
# def user_person(name: str):
#     """Get the user person for the given name

#     Args:
#         name (str): The name of the user person

#     Returns:
#         dict: The user person for the given name
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]
#     response = requests.get(
#         f"https://public-api.sandbox.bunq.com/v1/user-person/{user_id}",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.get("/user/{name}/monetary-account-bank", operation_id="get_monetary_account_bank")
# def monetary_account_bank(name: str):
#     """Get the monetary account bank for the given name

#     Args:
#         name (str): The name of the user
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]
#     response = requests.get(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account-bank",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.get("/user/{name}/monetary-account/{monetaryAccountId}/payment", operation_id="get_payment_from_monetary_account")
# def payment(name: str, monetaryAccountId: str):
#     """Get the payment for the given name and monetaryAccountId

#     Args:
#         name (str): The name of the user
#         monetaryAccountId (str): The monetaryAccountId of the user
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]
#     response = requests.get(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account/{monetaryAccountId}/payment",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.get("/user/{name}/event", operation_id="get_event_user")
# def event(name: str):
#     """Get the event for the given name

#     Args:
#         name (str): The name of the user
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]
#     response = requests.get(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/event",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.post("/user/{name}/card-credit", operation_id="create_card_credit_user")
# def card_credit(name: str):
#     """Get the card for the given name

#     Args:
#         name (str): The name of the user
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]   
#     response = requests.post(
#        f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/card-credit",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
#         data=json.dumps(
#             {"first_line":"text",
#              "second_line":"text",
#              "name_on_card":"text",
#              "preferred_name_on_card":"text",
#              "type":"MASTERCARD",
#              "product_type":"MAESTRO_DEBIT",
#              "monetary_account_id_fallback":1,
#              "order_status":"NEW_CARD_REQUEST_RECEIVED"
#              }),
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.post("/user/{name}/monetary-account-bank", operation_id="add_monetary_account_to_user")
# def add_monetary_account_to_user(name: str):
#     """Add a monetary account to the given name

#     Args:
#         name (str): The name of the user
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]
#     response = requests.post(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account-bank",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
#         data= json.dumps({"currency": "EUR"}),
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.post("/user/{name}/monetary-account/{monetaryAccountId}/payment", operation_id="add_money_to_account")
# def add_money_to_account(name: str, monetaryAccountId: str):
#     """Add money to the given name and monetaryAccountId

#     Args:
#         name (str): The name of the user
#         monetaryAccountId (str): The monetaryAccountId of the user
#     """
#     change_context(name)
#     user_id = name_to_uid[name]
#     token = uid_to_context[user_id][1]
#     response = requests.get(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id}/monetary-account/{monetaryAccountId}/request-inquiry",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Accept":"*/*"},
#         timeout=1000
#     )

#     data = response.json()
#     return data

# @app.post("/user/{name}/monetary-account/{monetaryAccountId}/payment", operation_id="pay_money_between_users")
# def pay_money_between_users(name1: str, monetaryAccountId1: str, name2: str, monetaryAccountId2: str, amount: float):
#     """Pay money between users

#     Args:
#         name1 (str): The name of the user getting money
#         monetaryAccountId1 (str): The monetaryAccountId of the user
#         name2 (str): The name of the user sending money
#         monetaryAccountId2 (str): The monetaryAccountId of the user sending money
#         amount (float): The amount of money to pay
#     """
#     print("pay_money_between_users")
#     print(name1)
#     change_context(name1)
#     print("context changed")
    
#     user_id1 = name_to_uid[name1]
#     token = uid_to_context[user_id1][1]
#     response1 = requests.post(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id1}/monetary-account/{monetaryAccountId1}/payment",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
#         data= json.dumps({"amount": amount}),
#         timeout=1000
#     )
#     change_context(name2)
#     user_id2 = name_to_uid[name2]
#     token = uid_to_context[user_id2][1]
#     response2 = requests.post(
#         f"https://public-api.sandbox.bunq.com/v1/user/{user_id2}/monetary-account/{monetaryAccountId2}/payment",
#         headers={"User-Agent":"text","X-Bunq-Client-Authentication":token,"Content-Type":"application/json"},
#         data= json.dumps({"amount": amount}),
#         timeout=1000
#     )
#     data1 = response1.json()
#     data2 = response2.json()
#     return data1, data2

# mcp = FastApiMCP(app)

# @app.on_event("startup")
# def startup_event():
#     mcp.mount()

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)