from fastapi import FastAPI
from models.misc import ChatRequest
from openai import OpenAI
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# initialize openai client
client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API")
)

app = FastAPI()

@app.post("/chat")
def chat(request: ChatRequest):
    
    completion = client.chat.completions.create(
        model="nvidia/llama-3.3-nemotron-super-49b-v1",
        messages=request.messages
    )
    
    return completion.choices[0].message.content
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)