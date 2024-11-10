from pydantic import BaseModel
from typing import Optional
from app.models.solar_assessment import SolarAssessmentResponse
from app.models.wind import WindDataResponse

class ChatRequest(BaseModel):
    message: str

# Define a response model for the chat response
class ChatResponse(BaseModel):
    response: str
    solar_assessment: Optional[SolarAssessmentResponse] = None
    wind_assessment: Optional[WindDataResponse] = None

# app/models/combined_assessment.py
from pydantic import BaseModel
from .solar_assessment import SolarAssessmentResponse
from .wind import WindDataResponse

class CombinedAssessmentRequest(BaseModel):
    city_name: str

class CombinedAssessmentResponse(BaseModel):
    solar_assessment: SolarAssessmentResponse
    wind_assessment: WindDataResponse
