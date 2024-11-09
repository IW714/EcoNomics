import requests
from fastapi import HTTPException
from app.utils.constants import NREL_UTILITY_RATES_URL
import os

NREL_API_KEY = os.getenv("NREL_API_KEY")

def get_utility_rates(lat: float, lon: float) -> dict:
    """
    Fetches utility rates for residential, commercial, and industrial sectors from NREL API.

    :param lat: Latitude of the location
    :param lon: Longitude of the location
    :return: Dictionary containing utility rates
    """
    params = {
        "format": "json", 
        "api_key": NREL_API_KEY,
        "lat": lat,
        "lon": lon
    }

    response = requests.get(NREL_UTILITY_RATES_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch utility rates data.")
    
    data = response.json()
    outputs = data.get("outputs")

    if not outputs: 
        raise HTTPException(status_code=500, detail="Utility rates data unavailable.")
    
    # Extract utility rates
    residential_rate = outputs.get("residential")
    commercial_rate = outputs.get("commercial")
    industrial_rate = outputs.get("industrial")

    if residential_rate is None: 
        raise HTTPException(status_code=500, detail="Residential utility rate unavailable.")

    return {
        "utility_name": outputs.get("utility_name"),
        "residential": residential_rate,
        "commercial": commercial_rate,
        "industrial": industrial_rate
    }
