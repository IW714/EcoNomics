# Define a request model for the chat message
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

# Define a response model for the chat response
class ChatResponse(BaseModel):
    response: str