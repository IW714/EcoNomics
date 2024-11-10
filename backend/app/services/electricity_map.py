import requests
from fastapi import HTTPException
from app.utils.constants import ELECTRICITYMAP_BASE_URL
import os
import logging

logger = logging.getLogger(__name__)

ELECTRICITYMAP_API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")
DEFAULT_CARBON_INTENSITY = 500.0  # Default value in gCO2eq/kWh

def get_carbon_intensity(lat: float, lon: float) -> float:
    """
    Fetches the carbon intensity for the given location from ElectricityMap API.
    Falls back to default value if API call fails.

    :param lat: Latitude of the location
    :param lon: Longitude of the location
    :return: Carbon intensity in gCO2eq/kWh
    """
    try:
        url = f"{ELECTRICITYMAP_BASE_URL}/carbon-intensity/latest"
        headers = {
            "auth-token": ELECTRICITYMAP_API_KEY
        }
        params = {
            "lat": lat,
            "lon": lon
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            carbon_intensity = data.get("carbonIntensity")
            if carbon_intensity is not None:
                return float(carbon_intensity)
        
        # If we get here, either the request failed or data was missing
        logger.warning(
            f"Using default carbon intensity ({DEFAULT_CARBON_INTENSITY} gCO2eq/kWh) for location "
            f"lat={lat}, lon={lon}. API Status: {response.status_code}"
        )
        return DEFAULT_CARBON_INTENSITY

    except Exception as e:
        logger.warning(
            f"Error fetching carbon intensity data: {str(e)}. Using default value "
            f"({DEFAULT_CARBON_INTENSITY} gCO2eq/kWh)"
        )
        return DEFAULT_CARBON_INTENSITY