# Define Pydantic models for request and response
from typing import Optional
from pydantic import BaseModel, Field


class WindDataRequest(BaseModel):
    lat: float = Field(..., example=55.626, description="Latitude of the location")
    lon: float = Field(..., example=1.496, description="Longitude of the location")
    height: int = Field(..., example=100, description="Height above ground level in meters")
    date_from: str = Field(..., example="2019-01-01", description="Start date in 'YYYY-MM-DD' format")
    date_to: str = Field(..., example="2019-01-31", description="End date in 'YYYY-MM-DD' format")

class WindDataResponse(BaseModel):
    total_energy_kwh: float = Field(..., description="Total Energy Generated (kWh)")
    capacity_factor_percentage: float = Field(..., description="Capacity Factor (%)")
    message: Optional[str] = Field(None, description="Status message")