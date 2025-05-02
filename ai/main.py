from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
import dotenv
import os
from utils.api_handler import fetch_bunq_users
from utils.api_handler import inspect_user_attributes
from utils.api_handler import fetch_monetary_accounts
from utils.api_handler import fetch_payments

dotenv.load_dotenv()

BUNQ_API = os.getenv("BUNQ_API")
NVIDIA_API = os.getenv("NVIDIA_API")

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
# print(inspect_user_attributes(1))
users = fetch_bunq_users(
    limit=20,  # Optional: specify how many users to fetch
    output_filename="my_bunq_users.json"  # Optional: custom filename
)

accounts = fetch_monetary_accounts(
    limit=20,  # Optional: specify how many accounts to fetch
    output_filename="my_bunq_accounts.json"  # Optional: custom filename
)

for account in accounts:
    payments = fetch_payments(
        account["id"],
        limit=20,  # Optional: specify how many payments to fetch
        output_filename="my_bunq_payments.json"  # Optional: custom filename
    )

# print(inspect_user_attributes(1))