import sys
import requests
import pandas as pd
import os
from datetime import datetime
from io import StringIO

def fetch_wind_data(lat, lon, height, date_from, date_to, output_file):
    """
    Retrieve wind speed data from a specified API and save it to a CSV file.

    Parameters:
    - lat (float): Latitude of the location.
    - lon (float): Longitude of the location.
    - height (int): Height above ground level in meters for wind data.
    - date_from (str): Start date in 'YYYY-MM-DD' format.
    - date_to (str): End date in 'YYYY-MM-DD' format.
    - output_file (str): Name of the output CSV file.
    """
    # Construct the API URL with parameters for location, height, and date range
    url = f"http://windatlas.xyz/api/wind/?lat={lat}&lon={lon}&height={height}&date_from={date_from}&date_to={date_to}"
    
    try:
        print(f"Sending request to Wind Atlas API for dates {date_from} to {date_to}...")
        
        # Send the request to the API and wait up to 60 seconds for a response
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # Raise an error if the request failed

        # Convert the CSV text from the response into a DataFrame
        # Skips the first line if it contains metadata
        df = pd.read_csv(StringIO(response.text), skiprows=1)
        print("Wind data successfully retrieved from API.")
        
        # Check that the required columns are present in the data
        if 'datetime' not in df.columns or 'wind_speed' not in df.columns:
            print("Error: Expected columns 'datetime' and 'wind_speed' not found in the data.")
            raise ValueError("Missing expected columns in wind data.")
        
        # Convert 'datetime' column to pandas datetime format, handling any conversion errors
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        print("Date format verified and converted successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve wind data: {e}")
        raise  # Re-raise exception for further handling if needed
    except Exception as e:
        print(f"An error occurred while processing wind data: {e}")
        raise

    # Attempt to save the DataFrame to a CSV file
    try:
        df.to_csv(output_file, index=False)
        print(f"Wind data successfully saved to '{output_file}'.")
    except Exception as e:
        print(f"Failed to save wind data to CSV: {e}")
        raise

def main():
    if len(sys.argv) != 6:
        print("Usage: fetch_wind_data.py <lat> <lon> <height> <date_from> <date_to>")
        sys.exit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    height = int(sys.argv[3])
    date_from = sys.argv[4]
    date_to = sys.argv[5]
    output_file = 'data/wind_data.csv'

    fetch_wind_data(lat, lon, height, date_from, date_to, output_file)
    print("Wind Data Retrieval Script Completed.")

if __name__ == "__main__":
    main()
