from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType
import dotenv
import os

dotenv.load_dotenv()

BUNQ_API = os.getenv("BUNQ_API")
NVIDIA_API = os.getenv("NVIDIA_API")

if not BUNQ_API:
    raise ValueError("BUNQ_API environment variable is not set. Please set it in your .env file.")
if not NVIDIA_API:
    raise ValueError("NVIDIA_API environment variable is not set. Please set it in your .env file.")

if os.path.exists("bunq_api_context.conf"):
    api_context = ApiContext.restore("bunq_api_context.conf")
else:
    # Create an API context for production
    api_context = ApiContext.create(ApiEnvironmentType.SANDBOX, BUNQ_API, "Hackathon")

    # Save the API context to a file for future use
    api_context.save("bunq_api_context.conf")

# Load the API context into the SDK
BunqContext.load_api_context(api_context)

user_context = BunqContext.user_context()


print("Welcome to the Bunq API!")
print(user_context.user_id)