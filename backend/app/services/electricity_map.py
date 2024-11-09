import requests
from fastapi import HTTPException
from app.utils.constants import ELECTRICITYMAP_BASE_URL
import os

ELECTRICITYMAP_API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")

# app/services/electricity_map.py

import requests
from fastapi import HTTPException
from app.utils.constants import ELECTRICITYMAP_BASE_URL
import os

ELECTRICITYMAP_API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")

def get_carbon_intensity(lat: float, lon: float) -> float:
    """
    Fetches the carbon intensity for the given location from ElectricityMap API.

    :param lat: Latitude of the location
    :param lon: Longitude of the location
    :return: Carbon intensity in gCO2eq/kWh
    """
    url = f"{ELECTRICITYMAP_BASE_URL}/carbon-intensity/latest"
    headers = {
        "auth-token": ELECTRICITYMAP_API_KEY
    }
    params = {
        "lat": lat,
        "lon": lon
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch carbon intensity data.")

    data = response.json()
    carbon_intensity = data.get("carbonIntensity")
    if carbon_intensity is None:
        raise HTTPException(status_code=500, detail="Carbon intensity data unavailable.")

    return carbon_intensity  # in gCO2eq/kWh TODO: This may need to be double checked
