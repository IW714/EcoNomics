import requests
from fastapi import HTTPException
from app.utils.constants import NREL_UTILITY_RATES_URL
import os
import logging

logger = logging.getLogger(__name__)

NREL_API_KEY = os.getenv("NREL_API_KEY")
DEFAULT_RATES = {
    "utility_name": "Default Utility",
    "residential": 0.12,  # Default residential rate in USD/kWh
    "commercial": 0.11,   # Default commercial rate in USD/kWh
    "industrial": 0.10    # Default industrial rate in USD/kWh
}

def get_utility_rates(lat: float, lon: float) -> dict:
    """
    Fetches utility rates for residential, commercial, and industrial sectors from NREL API.
    Falls back to default values if data is unavailable.

    :param lat: Latitude of the location
    :param lon: Longitude of the location
    :return: Dictionary containing utility rates
    """
    try:
        params = {
            "format": "json", 
            "api_key": NREL_API_KEY,
            "lat": lat,
            "lon": lon
        }

        response = requests.get(NREL_UTILITY_RATES_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            outputs = data.get("outputs")
            
            if outputs:
                residential_rate = outputs.get("residential")
                commercial_rate = outputs.get("commercial")
                industrial_rate = outputs.get("industrial")
                
                # Check if any of the rates are 'no data' or None
                if residential_rate not in [None, 'no data'] and \
                   commercial_rate not in [None, 'no data'] and \
                   industrial_rate not in [None, 'no data']:
                    return {
                        "utility_name": outputs.get("utility_name", DEFAULT_RATES["utility_name"]),
                        "residential": float(residential_rate),
                        "commercial": float(commercial_rate),
                        "industrial": float(industrial_rate)
                    }
        
        # If we get here, either the request failed or data was invalid
        logger.warning(
            f"Using default utility rates for location lat={lat}, lon={lon}. "
            f"API Status: {response.status_code}"
        )
        return DEFAULT_RATES

    except Exception as e:
        logger.warning(f"Error fetching utility rates data: {str(e)}. Using default values")
        return DEFAULT_RATES