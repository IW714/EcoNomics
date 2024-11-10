import math
import os
import aiohttp
import requests
import logging
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.solar_assessment import Location, LocationRequest, PVWattsRequest, SolarAssessmentRequest, SolarAssessmentResponse
from app.models.wind import WindDataRequest, WindDataResponse
from app.services.electricity_map import get_carbon_intensity
from app.services.nrel_pvwatts import get_pvwatts_data
from app.services.nrel_utility_rates import get_utility_rates
from app.calculations.solar_calculations import calculate_panel_area, calculate_cost_savings, calculate_roi, calculate_co2_reduction
from app.services.wind.fetch.fetch_era5_data import fetch_data as fetch_era5_data
from app.services.wind.calculate.calculate_air_density import calculate_air_density_from_nc
from app.services.wind.fetch.fetch_wind_data import fetch_wind_data
from app.calculations.wind_calculations import calculate_annual_wind_energy, calculate_wind_cost_savings
from app.services.wind.calculate.merge_and_calculate_power import calculate_wind_metrics, merge_and_calculate_power
from app.models.ai import ChatRequest, ChatResponse, CombinedAssessmentRequest, CombinedAssessmentResponse
import ssl
import certifi

# Set up logging
logger = logging.getLogger("wind_data_api")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI(title="Renewable Energy Assessment API")

# CORS setup
origins = ["http://localhost:5173", 
           "http://localhost:5174"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Geocoding API setup
GEOCODING_API_KEY = os.getenv("GEOCODE_API_KEY")
GEOCODING_API_URL = "https://api.opencagedata.com/geocode/v1/json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.post("/get_coordinates", response_model=Location)
async def get_coordinates(location: LocationRequest):
    try:
        response = requests.get(GEOCODING_API_URL, params={
            "q": location.city_name,
            "key": GEOCODING_API_KEY,
            "limit": 1
        })
        data = response.json()
        
        if data["results"]:
            coordinates = data["results"][0]["geometry"]
            return Location(latitude=coordinates["lat"], longitude=coordinates["lng"])
        else:
            raise HTTPException(status_code=404, detail="Location not found")
    except Exception as e:
        logger.error(f"Error fetching coordinates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/calculate_solar_potential", response_model=SolarAssessmentResponse)
def calculate_solar_potential(request: SolarAssessmentRequest):
    try:
        # If a city name is provided, fetch coordinates
        if request.city_name:
            response = requests.post("http://127.0.0.1:8000/get_coordinates", json={"city_name": request.city_name})
            response_data = response.json()
            
            if response.status_code != 200 or "latitude" not in response_data or "longitude" not in response_data:
                raise HTTPException(status_code=404, detail="City not found or coordinates unavailable.")
            
            lat, lon = response_data["latitude"], response_data["longitude"]
        else:
            lat, lon = request.latitude, request.longitude

        if lat == 0.0 and lon == 0.0:
            raise HTTPException(status_code=400, detail="Invalid coordinates provided")
        
        pvwatts_request = PVWattsRequest(
            system_capacity=4.0, module_type=0, losses=14.0,
            array_type=1, tilt=10.0, azimuth=180.0,
            location=Location(latitude=lat, longitude=lon)
        )
        
        # Get the data from PVWatts
        pv_outputs = get_pvwatts_data(pvwatts_request)
        ac_annual = pv_outputs.get("ac_annual")
        solrad_annual = pv_outputs.get("solrad_annual")
        capacity_factor_percentage = pv_outputs.get("capacity_factor")

        if ac_annual is None or solrad_annual is None or capacity_factor_percentage is None:
            raise HTTPException(status_code=500, detail="Incomplete PVWatts data received.")

        # Convert everything to float and handle list/tuple cases
        capacity_factor = float(capacity_factor_percentage) / 100
        solrad_annual = float(solrad_annual)
        carbon_intensity = get_carbon_intensity(lat, lon)  # Will now use default value if API fails
        utility_rates = get_utility_rates(lat, lon)
        energy_price = float(utility_rates.get("residential", 0.1))

        system_efficiency = 1 - (pvwatts_request.losses / 100)
        panel_efficiency = 0.18
        
        # If ac_annual is a list, use the first value for dc_annual calculation
        ac_annual_value = ac_annual[0] if isinstance(ac_annual, (list, tuple)) else ac_annual
        dc_annual = float(ac_annual_value) / system_efficiency
        
        panel_area = calculate_panel_area(dc_annual, solrad_annual, panel_efficiency)
        annual_cost_savings = calculate_cost_savings(ac_annual, energy_price)
        initial_cost = pvwatts_request.system_capacity * 2500
        roi_years = calculate_roi(initial_cost, annual_cost_savings)
        emission_factor = carbon_intensity / 1000  # Convert to kg CO2/kWh
        co2_reduction = calculate_co2_reduction(ac_annual, emission_factor)

        # Use ac_annual_value for the response
        return SolarAssessmentResponse(
            ac_annual=float(ac_annual_value),
            solrad_annual=solrad_annual,
            capacity_factor=capacity_factor,
            panel_area=panel_area,
            annual_cost_savings=annual_cost_savings,
            roi_years=roi_years,
            co2_reduction=co2_reduction
        )

    except HTTPException as he:
        logger.error(f"HTTPException occurred: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in solar calculations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in solar calculations: {str(e)}")
    
@app.post("/process_wind_data", response_model=WindDataResponse)
def process_wind_data(request: WindDataRequest):
    try:
        # Handle coordinates
        if request.city_name:
            response = requests.post("http://127.0.0.1:8000/get_coordinates", json={"city_name": request.city_name})
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="City not found.")
            response_data = response.json()
            lat, lon = response_data.get("latitude"), response_data.get("longitude")
        else:
            lat, lon = request.lat, request.lon

        if lat is None or lon is None or (lat == 0.0 and lon == 0.0):
            raise HTTPException(status_code=400, detail="Invalid coordinates provided.")

        year, month, day = request.date_from.split('-')

        try:
            # Fetch required data
            fetch_era5_data(lat, lon, buffer_deg=0.25, year=year, month=month, day=day)
            calculate_air_density_from_nc()
            fetch_wind_data(lat, lon, request.height, request.date_from, request.date_to)
            
            # Calculate power output
            df_power = merge_and_calculate_power(
                wind_data_file='data/wind_data.csv',
                air_density_file='data/air_density_january_2019.csv',
                output_file='data/merged_power_data.csv'
            )
            
            # Get utility rate
            energy_price = float(get_utility_rates(lat, lon).get("residential", 0.12))
            
            # Calculate all metrics
            metrics = calculate_wind_metrics(df_power, energy_price)
            
            # Return response matching the WindDataResponse model
            return WindDataResponse(
                total_energy_kwh=metrics["total_energy_kwh"],
                capacity_factor_percentage=metrics["capacity_factor_percentage"],
                cost_savings=metrics["annual_savings"],  # This matches the 'cost_savings' field in the model
                payback_period=metrics.get("payback_period"),  # Optional
                co2_reduction=metrics.get("co2_reduction")     # Optional
            )

        except requests.HTTPError as http_err:
            if "500 Server Error" in str(http_err):
                raise HTTPException(
                    status_code=404,
                    detail="We currently don't have coverage in this location."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Wind data API is currently unavailable. Please try again later."
                )

    except HTTPException as he:
        logger.error(f"HTTPException occurred: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in wind calculations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _call_openai(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        # Create the SSL context with the default trusted certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]
    except aiohttp.ClientResponseError as e:
        logger.error(f"Error communicating with OpenAI API: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with OpenAI API")
    
@app.post("/chat", response_model=ChatResponse)
async def chat_with_openai(request: ChatRequest):
    user_message = request.message.lower().strip()

    # Ask the model if we should run the energy assessment functions
    try:
        should_run_assessment = await _should_run_energy_assessment(user_message)
    except Exception as e:
        logger.error(f"Error in _should_run_energy_assessment: {e}")
        return ChatResponse(response="Error: Unable to determine if energy assessment should be run. Please try again later.")

    if should_run_assessment:
        try:
            # Run the combined assessment
            city_name = user_message.replace("calculate energy in", "").strip()
            combined_result = await combined_assessment(CombinedAssessmentRequest(city_name=city_name))

            # Format the response with detailed analysis
            solar_assessment = combined_result.solar_assessment
            wind_assessment = combined_result.wind_assessment

            # Solar assessment analysis
            solar_analysis = (
                f"Solar Assessment for {city_name}:\n"
                f"- Annual AC Output: {solar_assessment.ac_annual:.2f} kWh\n"
                f"- Solar Radiation: {solar_assessment.solrad_annual:.2f} kWh/m²/day\n"
                f"- Capacity Factor: {solar_assessment.capacity_factor * 100:.2f}%\n"
                f"- Estimated Panel Area: {solar_assessment.panel_area:.2f} m²\n"
                f"- Estimated Annual Cost Savings: ${solar_assessment.annual_cost_savings:.2f}\n"
                f"- Estimated Payback Period: {solar_assessment.roi_years:.2f} years\n"
                f"- Estimated CO2 Reduction: {solar_assessment.co2_reduction:.2f} kg/year\n"
            )

            # Wind assessment analysis
            wind_analysis = (
                f"Wind Assessment for {city_name}:\n"
                f"- Annual Energy Output: {wind_assessment.total_energy_kwh:.2f} kWh\n"
                f"- Capacity Factor: {wind_assessment.capacity_factor_percentage:.2f}%\n"
                f"- Estimated Annual Cost Savings: ${wind_assessment.cost_savings:.2f}\n"
            )

            if wind_assessment.message:
                wind_analysis += f"\nNote: {wind_assessment.message}"

            response = (
                f"Energy assessment for {city_name}:\n\n"
                f"{solar_analysis}\n\n{wind_analysis}"
            )

            return ChatResponse(response=response)

        except Exception as e:
            logger.error(f"Failed to perform assessment: {e}")
            return ChatResponse(response="Error: Unable to perform energy assessment. Please try again.")
    else:
        try:
            assistant_message = await _call_openai(request.message.strip())
            return ChatResponse(response=assistant_message)
        except requests.RequestException as e:
            logger.error(f"Error communicating with OpenAI API: {e}")
            raise HTTPException(status_code=500, detail="Error communicating with OpenAI API")
        
async def _should_run_energy_assessment(user_message: str) -> bool:
    # Use the model to determine if we should run the energy assessment functions
    prompt = f"Given the user's message '{user_message}', should we run the energy assessment functions? Respond with either 'yes' or 'no'."
    response = await _call_openai(prompt)
    return response.lower().strip() == "yes"

@app.post("/combined_assessment", response_model=CombinedAssessmentResponse)
async def combined_assessment(request: CombinedAssessmentRequest):
    try:
        # Step 1: Fetch coordinates for the city
        coordinates_response = await get_coordinates(LocationRequest(city_name=request.city_name))
        lat, lon = coordinates_response.latitude, coordinates_response.longitude

        # Step 2: Perform solar assessment
        solar_assessment_request = SolarAssessmentRequest(latitude=lat, longitude=lon)
        solar_result = calculate_solar_potential(solar_assessment_request)

        # Step 3: Perform wind assessment
        wind_assessment_request = WindDataRequest(lat=lat, lon=lon, height=100, date_from="2019-01-01", date_to="2019-01-31")
        wind_result = process_wind_data(wind_assessment_request)

        # Step 4: Return combined results
        return CombinedAssessmentResponse(
            solar_assessment=solar_result,
            wind_assessment=wind_result
        )

    except HTTPException as he:
        logger.error(f"HTTPException occurred: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in combined assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error in combined assessment")