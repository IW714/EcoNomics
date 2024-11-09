from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models.solar_assessment import SolarAssessmentRequest, SolarAssessmentResponse
from app.services.electricity_map import get_carbon_intensity
from app.services.nrel_pvwatts import get_pvwatts_data
from app.services.nrel_utility_rates import get_utility_rates
from app.calculations.solar_calculations import (
    calculate_panel_area,
    calculate_cost_savings,
    calculate_roi,
    calculate_co2_reduction
)
from app.utils.constants import DEFAULT_EMISSION_FACTOR
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Renewable Energy Assessment API")

# Configure CROS
origins = [
    "http://localhost:5173", # React frontend
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all HTTP headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/calculate_solar_potential", response_model=SolarAssessmentResponse)
def calculate_solar_potential(request: SolarAssessmentRequest):
    """
    Calculates the annual solar potential, energy saving costs, ROI, and CO2 reductions.

    :param request: SolarAssessmentRequest containing PVWatts and Utility Rates data
    :return: SolarAssessmentResponse with calculated metrics
    """
    try: 
        lat = request.pvwatts.location.latitude
        lon = request.pvwatts.location.longitude

        # Fetch PVWatts data
        pv_outputs = get_pvwatts_data(request.pvwatts.model_dump())

        # Extract necessary fields from PVWatts output 
        ac_annual = pv_outputs.get("ac_annual") # kWhac
        solrad_annual = pv_outputs.get("solrad_annual") # kWh/m²/day
        capacity_factor_percentage = pv_outputs.get("capacity_factor") # AC-to-DC ratio

        if ac_annual is None or solrad_annual is None or capacity_factor_percentage is None:
            raise HTTPException(status_code=500, detail="Incomplete PVWatts data received.")
        
        capacity_factor = capacity_factor_percentage / 100  # Convert percentage to ratio
        logger.info(f"Capacity Factor (Ratio): {capacity_factor}")      

        # Fetch carbon intensity
        carbon_intensity = get_carbon_intensity(lat, lon) # gCO2eq/kWh

        # Fetch utility rates
        utility_rates = get_utility_rates(lat, lon)

        # Choose the appropriate energy price
        # TODO: Expand to allow user selection
        energy_price = utility_rates.get("residential") # USD/kWh
        if energy_price is None:
            raise HTTPException(status_code=500, detail="Residential utility rate unavailable.")
        
        # Calculate system efficency from losses
        losses = request.pvwatts.losses  # in percentage
        if losses < 0 or losses >= 100:
            raise HTTPException(status_code=400, detail="Losses must be between 0 and 100 percent.")
        system_efficiency = 1 - (losses / 100)  # e.g., 14% losses => 0.86 efficiency

        # Define panel efficiency
        panel_efficiency = 0.18  # Typically range from 15% to 20%

        # Calculate effective efficiency
        # effective_efficiency = system_efficiency * panel_efficiency

        # Calculate panel area
        dc_annual = ac_annual / system_efficiency
        logger.info(f"DC Annual Output: {dc_annual} kWhdc")
        panel_area = calculate_panel_area(dc_annual, solrad_annual, panel_efficiency)
        logger.info(f"Required Panel Area: {panel_area} m²")

        # Calculate annual cost savings
        annual_cost_savings = calculate_cost_savings(ac_annual, energy_price)

        # Calculate ROI
        # Assuming initial_cost is based on system_capacity. This can be made more precise with detailed inputs.
        # Example: $4,000 per kW installed
        initial_cost = request.pvwatts.system_capacity * 2500  # USD TODO: might need to allow users to adjust initial costs
        roi_years = calculate_roi(initial_cost, annual_cost_savings)

        # Calculate CO2 reduction
        # Convert carbon intensity from gCO2eq/kWh to kgCO2eq/kWh
        emission_factor = carbon_intensity / 1000  # kg CO2/kWh
        logger.info(f"Emission Factor: {emission_factor} kg CO2/kWh")
        co2_reduction = calculate_co2_reduction(ac_annual, emission_factor)
        logger.info(f"Annual CO2 Reduction: {co2_reduction} kg")

        response = SolarAssessmentResponse(
            ac_annual=ac_annual,                        # kWhac
            solrad_annual=solrad_annual,                # kWh/m²/day
            capacity_factor=capacity_factor,            # AC-to-DC ratio
            panel_area=panel_area,                      # m²   
            annual_cost_savings=annual_cost_savings,    # USD
            roi_years=roi_years,                        # years
            co2_reduction=co2_reduction                 # kg
        )

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




    
    