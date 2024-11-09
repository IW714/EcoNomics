from pydantic import BaseModel, Field
from typing import Optional

class Location(BaseModel): 
    latitude: float = Field(..., example=37.7749)
    longitude: float = Field(..., example=-122.4194)

class PVWattsRequest(BaseModel):
    system_capacity: float = Field(..., example=4.0, description="System capacity in kW")
    module_type: int = Field(..., example=0, description="Module type (0=Standard, 1=Premium, 2=Thin Film)")
    losses: float = Field(..., example=14.0, description="System losses in percentage")
    array_type: int = Field(..., example=1, description="Array type (1=Fixed (open rack), 2=Fixed (roof mount), etc.)")
    tilt: float = Field(..., example=10.0, description="Tilt angle of the array in degrees")
    azimuth: float = Field(..., example=180.0, description="Azimuth angle of the array in degrees")
    location: Location

class UtilityRatesRequest(BaseModel):
    location: Location

class SolarAssessmentRequest(BaseModel):
    pvwatts: PVWattsRequest
    utility_rates: UtilityRatesRequest

class SolarAssessmentResponse(BaseModel):
    ac_annual: float = Field(..., description="Annual AC system output (kWhac)")
    solrad_annual: float = Field(..., description="Annual solar radiation (kWh/m²/day)")
    capacity_factor: float = Field(..., description="Capacity factor (AC-to-DC)")
    panel_area: float = Field(..., description="Required panel area (m²)")
    annual_cost_savings: float = Field(..., description="Annual cost savings (USD)")
    roi_years: float = Field(..., description="Return on Investment (years)")
    co2_reduction: float = Field(..., description="Annual CO2 reduction (kg)")