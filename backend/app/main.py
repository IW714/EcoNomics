import math
from fastapi import FastAPI, HTTPException, Depends, logger
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
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

from app.models.wind import WindDataRequest, WindDataResponse
from app.services.wind.calculate import merge_and_calculate_power
from app.services.wind.calculate.calculate_air_density import calculate_air_density, calculate_air_density_from_nc
from app.services.wind.calculate.calculate_capacity_factor import calculate_capacity_factor, calculate_capacity_factor_from_csv
from app.services.wind.fetch import fetch_era5_data, fetch_wind_data

# Set up logger
logger = logging.getLogger("wind_data_api")
logger.setLevel(logging.INFO)

# Create handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)


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
    
    # Issue that needs to be resolved is that there are some areas in which
    # the wind data does not exist# Threshold in kilometers for significant location change
    
LOCATION_THRESHOLD_KM = 50
LAST_LOCATION_FILE = 'data/last_location.csv'

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    Returns the distance in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def location_has_changed(lat, lon):
    """
    Check if the location has changed beyond the defined threshold.
    """
    if os.path.exists(LAST_LOCATION_FILE):
        last_data = pd.read_csv(LAST_LOCATION_FILE)
        last_lat, last_lon = last_data.iloc[0]['latitude'], last_data.iloc[0]['longitude']
        distance = haversine(last_lat, last_lon, lat, lon)
        return distance > LOCATION_THRESHOLD_KM
    return True  # No previous data, so treat as changed

@app.post("/process_wind_data", response_model=WindDataResponse)
def process_wind_data(request: WindDataRequest):
    """
    Processes wind data based on the provided parameters and returns the results.
    """
    try:
        # Check if location change exceeds threshold
        if not location_has_changed(request.lat, request.lon):
            # Location has not changed significantly; load previous results if available
            merged_power_file = 'data/merged_power_data.csv'
            capacity_factor_file = 'data/capacity_factor.txt'
            
            if os.path.exists(merged_power_file) and os.path.exists(capacity_factor_file):
                df_power = pd.read_csv(merged_power_file)
                total_energy = df_power['energy_kwh'].sum()

                with open(capacity_factor_file, 'r') as f:
                    capacity_factor = float(f.read().split(":")[1].strip().strip('%'))

                # Return cached response
                return WindDataResponse(
                    total_energy_kwh=total_energy,
                    capacity_factor_percentage=capacity_factor,
                    message="Loaded previous results as location has not changed significantly."
                )
            else:
                raise HTTPException(status_code=500, detail="Previous results not found.")

        # Step 1: Fetch ERA5 Data
        fetch_era5_data.main(request.lat, request.lon, request.height, request.date_from, request.date_to)

        # Step 2: Calculate Air Density
        calculate_air_density_from_nc()

        # Step 3: Fetch Wind Data
        fetch_wind_data.main(request.lat, request.lon, request.height, request.date_from, request.date_to)

        # Step 4: Merge and Calculate Power
        merge_and_calculate_power.main()

        # Step 5: Calculate Capacity Factor
        capacity_factor = calculate_capacity_factor_from_csv()

        # Step 6: Calculate Total Energy Generated
        merged_power_file = 'data/merged_power_data.csv'
        if not os.path.exists(merged_power_file):
            raise HTTPException(status_code=500, detail="Merged power data file not found.")

        df_power = pd.read_csv(merged_power_file)
        total_energy = df_power['energy_kwh'].sum()

        # Save the new location and response data for future reference
        pd.DataFrame({'latitude': [request.lat], 'longitude': [request.lon]}).to_csv(LAST_LOCATION_FILE, index=False)
        
        with open('data/capacity_factor.txt', 'w') as f:
            f.write(f"Capacity Factor: {capacity_factor:.2f}%\n")

        # Prepare response
        response = WindDataResponse(
            total_energy_kwh=total_energy,
            capacity_factor_percentage=capacity_factor,
            message="Wind data processing completed successfully."
        )

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))