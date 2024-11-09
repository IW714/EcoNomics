import math
from fastapi import FastAPI, HTTPException, Depends, logger
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel
from app.models.solar_assessment import Location, PVWattsRequest, SolarAssessmentRequest, SolarAssessmentResponse
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
    "http://localhost:5174", # React frontend
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
    """
    try:
        lat = request.latitude
        lon = request.longitude

        # Log incoming request
        logger.info(f"Calculating solar potential for coordinates: Latitude={lat}, Longitude={lon}")

        # Define default PV system settings and instantiate PVWattsRequest
        pvwatts_request = PVWattsRequest(
            system_capacity=4.0,     # kW
            module_type=0,           # Standard module
            losses=14.0,             # System losses in percentage
            array_type=1,            # Fixed (open rack)
            tilt=10.0,               # Tilt angle in degrees
            azimuth=180.0,           # Azimuth angle in degrees
            location=Location(latitude=lat, longitude=lon)
        )

        # Fetch PVWatts data
        logger.info("Requesting PVWatts data from NREL API.")
        pv_outputs = get_pvwatts_data(pvwatts_request)
        
        # Log PVWatts response
        logger.debug(f"PVWatts data received: {pv_outputs}")

        # Extract necessary fields from PVWatts output
        ac_annual = pv_outputs.get("ac_annual")
        solrad_annual = pv_outputs.get("solrad_annual")
        capacity_factor_percentage = pv_outputs.get("capacity_factor")

        # Check if necessary data exists and log the values
        if ac_annual is None or solrad_annual is None or capacity_factor_percentage is None:
            logger.error("Incomplete PVWatts data received.")
            raise HTTPException(status_code=500, detail="Incomplete PVWatts data received.")
        
        capacity_factor = capacity_factor_percentage / 100
        logger.info(f"Capacity Factor (Ratio): {capacity_factor}")

        # Fetch carbon intensity
        logger.info("Fetching carbon intensity data.")
        carbon_intensity = get_carbon_intensity(lat, lon)
        logger.debug(f"Carbon Intensity: {carbon_intensity} gCO2eq/kWh")

        # Fetch utility rates
        logger.info("Fetching utility rates.")
        utility_rates = get_utility_rates(lat, lon)
        logger.debug(f"Utility Rates: {utility_rates}")

        # Choose the appropriate energy price
        energy_price = utility_rates.get("residential")
        if energy_price is None:
            logger.error("Residential utility rate unavailable.")
            raise HTTPException(status_code=500, detail="Residential utility rate unavailable.")
        logger.info(f"Energy Price (USD/kWh): {energy_price}")

        # Calculate system efficiency from losses
        losses = pvwatts_request.losses
        if losses < 0 or losses >= 100:
            logger.error("Losses must be between 0 and 100 percent.")
            raise HTTPException(status_code=400, detail="Losses must be between 0 and 100 percent.")
        system_efficiency = 1 - (losses / 100)
        logger.info(f"System Efficiency: {system_efficiency}")

        # Panel efficiency and calculation logs
        panel_efficiency = 0.18
        logger.info(f"Panel Efficiency: {panel_efficiency}")
        dc_annual = ac_annual / system_efficiency
        logger.debug(f"DC Annual Output: {dc_annual} kWhdc")

        # Calculate required panel area
        panel_area = calculate_panel_area(dc_annual, solrad_annual, panel_efficiency)
        logger.info(f"Required Panel Area: {panel_area} m²")

        # Calculate cost savings and ROI
        annual_cost_savings = calculate_cost_savings(ac_annual, energy_price)
        initial_cost = pvwatts_request.system_capacity * 2500
        roi_years = calculate_roi(initial_cost, annual_cost_savings)
        logger.info(f"Annual Cost Savings: {annual_cost_savings} USD")
        logger.info(f"Return on Investment (ROI): {roi_years} years")

        # Calculate CO2 reduction
        emission_factor = carbon_intensity / 1000
        co2_reduction = calculate_co2_reduction(ac_annual, emission_factor)
        logger.info(f"Annual CO2 Reduction: {co2_reduction} kg")

        # Prepare response with logging
        response = SolarAssessmentResponse(
            ac_annual=ac_annual,
            solrad_annual=solrad_annual,
            capacity_factor=capacity_factor,
            panel_area=panel_area,
            annual_cost_savings=annual_cost_savings,
            roi_years=roi_years,
            co2_reduction=co2_reduction
        )
        logger.info("Solar potential calculation completed successfully.")
        logger.debug(f"Response payload: {response.json()}")

        return response

    except HTTPException as he:
        logger.error(f"HTTPException occurred: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
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