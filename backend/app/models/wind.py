from pydantic import BaseModel, Field
from typing import Optional

class WindDataRequest(BaseModel):
    city_name: Optional[str] = Field(None, description="Name of the city for which to fetch data")
    lat: Optional[float] = Field(None, example=55.626, description="Latitude of the location")
    lon: Optional[float] = Field(None, example=1.496, description="Longitude of the location")
    height: int = Field(100, example=100, description="Height above ground level in meters")
    date_from: str = Field(..., example="2019-01-01", description="Start date in 'YYYY-MM-DD' format")
    date_to: str = Field(..., example="2019-01-31", description="End date in 'YYYY-MM-DD' format")

class WindDataResponse(BaseModel):
    total_energy_kwh: float = Field(..., description="Total Energy Generated (kWh)")
    capacity_factor_percentage: float = Field(..., description="Capacity Factor (%)")
    cost_savings: float = Field(..., description="Annual Cost Savings (USD)")
    payback_period: Optional[float] = Field(None, description="Payback Period (years)")
    co2_reduction: Optional[float] = Field(None, description="Annual CO2 Reduction (kg)")