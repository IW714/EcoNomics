# Define a request model for the chat message
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

# Define a response model for the chat response
class ChatResponse(BaseModel):
    response: str

# app/models/combined_assessment.py
from pydantic import BaseModel
from .solar_assessment import SolarAssessmentResponse
from .wind import WindDataResponse

class CombinedAssessmentRequest(BaseModel):
    city_name: str

class CombinedAssessmentResponse(BaseModel):
    solar_assessment: SolarAssessmentResponse
    wind_assessment: WindDataResponse
