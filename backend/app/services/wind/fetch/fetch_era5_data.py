import sys
import cdsapi
import os
from dotenv import load_dotenv


sys.path.append('/Users/westonvoglesonger/Projects/EcoNomics/backend')

from app.utils.constants import CDS_API_URL

# Load environment variables from .env file
load_dotenv()
cdsapi_key = os.getenv("CDSAPI_KEY")

def get_bounding_box(lat, lon, buffer_deg=0.25):
    north = min(lat + buffer_deg, 90)
    south = max(lat - buffer_deg, -90)
    east = min(lon + buffer_deg, 180)
    west = max(lon - buffer_deg, -180)
    return [north, west, south, east]

def fetch_data(lat, lon, buffer_deg, year, month, day, output_dir='data/'):
    c = cdsapi.Client(url=CDS_API_URL, key=cdsapi_key)
    
    area = get_bounding_box(lat, lon, buffer_deg)
    print(f"Bounding Box: North={area[0]}, West={area[1]}, South={area[2]}, East={area[3]}")

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'era5.nc')

    if os.path.exists(output_file):
        print(f"Data for {year}-{month}-{day} already exists at '{output_file}'. Skipping download.")
        return

    try:
        print(f"Starting data retrieval for {year}-{month}-{day}...")
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': [
                    '2m_temperature',
                    '2m_dewpoint_temperature',
                    'surface_pressure',
                ],
                'year': year,
                'month': month,
                'day': day,
                'time': ["12:00"],  # Use a list even for a single time
                'area': area,
                'format': 'netcdf',
            },
            output_file
        )
        print(f"Data retrieval successful. File saved as '{output_file}'.")
    except Exception as e:
        print(f"Data retrieval failed: {e}")
        raise

def main(lat, lon, height, date_from, date_to):
    year, month, day = date_from.split('-')
    fetch_data(lat, lon, 0.25, year, month, day)
    print("ERA5 Data Retrieval Completed.")