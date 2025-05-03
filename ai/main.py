from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
from dotenv import load_dotenv
import os
from utils.api_handler import fetch_bunq_users
from utils.api_handler import inspect_user_attributes
from utils.api_handler import fetch_monetary_accounts
from utils.api_handler import fetch_payments

load_dotenv()

BUNQ_API = "sandbox_572128f0229924f19cf33bfd7c3fc75e7427ad9ef3d9bc4b6b544fed"
NVIDIA_API = os.getenv("NVIDIA_API")

print(BUNQ_API)

if not BUNQ_API:
    raise ValueError("BUNQ_API environment variable is not set. Please set it in your .env file.")
if not NVIDIA_API:
    raise ValueError("NVIDIA_API environment variable is not set. Please set it in your .env file.")

if os.path.exists("bunq_api_context.conf"):
    os.remove("bunq_api_context.conf")

# else:
    # Create an API context for production
api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, BUNQ_API, "Hackathon")

    # Save the API context to a file for future use
api_context.save("bunq_api_context.conf")

# Load the API context into the SDK
BunqContext.load_api_context(api_context)

user_context = BunqContext.user_context()


print("Welcome to the Bunq API!")
print(user_context.user_id)
print(inspect_user_attributes(1).keys())

# users = fetch_bunq_users(
#     limit=20,  # Optional: specify how many users to fetch
#     output_filename="my_bunq_users.json"  # Optional: custom filename
# )
# print(users)
# accounts = fetch_monetary_accounts(
#     users[0]["name"],
#     limit=20,  # Optional: specify how many accounts to fetch
#     output_filename="my_bunq_accounts.json"  # Optional: custom filename
# )

# for account in accounts:
#     payments = fetch_payments(
#         users[0]["name"], 
#         account["id"],
#         limit=20,  # Optional: specify how many payments to fetch
#         output_filename="my_bunq_payments.json"  # Optional: custom filename
#     )

# print(inspect_user_attributes(1))