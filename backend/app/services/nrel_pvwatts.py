import requests
from fastapi import HTTPException
from app.utils.constants import NREL_PVWatts_BASE_URL
from app.models.solar_assessment import PVWattsRequest
from dotenv import load_dotenv
import os
import logging

load_dotenv()

NREL_API_KEY = os.getenv("NREL_API_KEY")

def get_pvwatts_data(pv_request: PVWattsRequest) -> dict:
    """
    Fetches PVWatts solar potential data from NREL API.

    :param pv_request: PVWattsRequest object containing system specifications and location
    :return: Dictionary containing PVWatts output data
    """
    params = {
        "format": "json",
        "api_key": NREL_API_KEY,
        "system_capacity": pv_request.system_capacity,
        "module_type": pv_request.module_type,
        "losses": pv_request.losses,
        "array_type": pv_request.array_type,
        "tilt": pv_request.tilt,
        "azimuth": pv_request.azimuth,
        "lat": pv_request.location.latitude,
        "lon": pv_request.location.longitude
    }

    response = requests.get(NREL_PVWatts_BASE_URL, params=params)
    if response.status_code != 200:
        logging.error(f"PVWatts API call failed. Status Code: {response.status_code}, Response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch PVWatts data.")

    data = response.json()
    outputs = data.get("outputs")
    if not outputs:
        raise HTTPException(status_code=500, detail="PVWatts output data unavailable.")

    return outputs
