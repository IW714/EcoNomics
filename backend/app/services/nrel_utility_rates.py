import requests
from fastapi import HTTPException
from app.utils.constants import NREL_UTILITY_RATES_URL
import os

NREL_API_KEY = os.getenv("NREL_API_KEY")
