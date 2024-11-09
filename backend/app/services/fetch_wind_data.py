# fetch_wind_data.py

import requests
import pandas as pd
import logging
import os
from datetime import datetime
from io import StringIO

def setup_logging():
    """
    Sets up logging configuration.
    Logs are saved to 'fetch_wind_data.log' and also printed to the console.
    """
    logging.basicConfig(
        filename='fetch_wind_data.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def fetch_wind_data(lat, lon, height, date_from, date_to, output_file='wind_data.csv'):
    """
    Retrieve wind speed data from the Wind Atlas API and save it to a CSV file.
    
    Parameters:
    - lat (float): Latitude of the location.
    - lon (float): Longitude of the location.
    - height (float): Wind measurement height in meters.
    - date_from (str): Start date in 'YYYY-MM-DD' format.
    - date_to (str): End date in 'YYYY-MM-DD' format.
    - output_file (str): Name of the output CSV file.
    """
    url = "http://windatlas.xyz/api/wind/"
    
    params = {
        'lat': lat,
        'lon': lon,
        'height': height,
        'date_from': date_from,
        'date_to': date_to,
        'format': 'csv'
    }

    try:
        logging.info(f"Sending request to Wind Atlas API for dates {date_from} to {date_to}...")
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Read CSV data, skipping the first line with metadata
        df = pd.read_csv(StringIO(response.text), skiprows=1)
        logging.info("Wind data successfully retrieved from API.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve wind data: {e}")
        raise
    except Exception as e:
        logging.error(f"Failed to parse CSV data: {e}")
        raise

    # Verify the expected columns
    expected_columns = ['datetime', 'wind_speed']
    existing_columns = df.columns.tolist()
    logging.info(f"Columns retrieved from API: {existing_columns}")

    if all(column in existing_columns for column in expected_columns):
        logging.info("Found 'datetime' and 'wind_speed' columns.")
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    else:
        logging.error("Required columns 'datetime' and 'wind_speed' not found. Cannot proceed.")
        raise ValueError("Missing required columns in wind data.")

    # Check for any NaT values in 'datetime'
    if df['datetime'].isnull().any():
        logging.warning("Some 'datetime' entries could not be parsed and are set as NaT.")
        df.dropna(subset=['datetime'], inplace=True)
        logging.info("Dropped rows with invalid 'datetime' entries.")

    # Save the cleaned DataFrame to CSV
    try:
        df.to_csv(output_file, index=False)
        logging.info(f"Wind data successfully saved to '{output_file}'.")
    except Exception as e:
        logging.error(f"Failed to save wind data to CSV: {e}")
        raise

def main():
    setup_logging()
    logging.info("Wind Data Retrieval Script Started.")

    # User inputs
    try:
        lat = 51.626
        lon = 1.496
        height = 100
        date_from = '2019-01-01'
        date_to = '2019-01-31'
    except ValueError as ve:
        logging.error(f"Invalid input: {ve}")
        return

    # Validate dates
    try:
        datetime.strptime(date_from, '%Y-%m-%d')
        datetime.strptime(date_to, '%Y-%m-%d')
    except ValueError:
        logging.error("Incorrect date format. Please use YYYY-MM-DD.")
        return

    # Define output file name based on dates
    output_file = f'wind_data.csv'

    # Check if file already exists to prevent redundant downloads
    if os.path.exists(output_file):
        logging.info(f"Wind data for {date_from} to {date_to} already exists at '{output_file}'. Skipping download.")
        return

    # Fetch wind data
    try:
        fetch_wind_data(lat, lon, height, date_from, date_to, output_file)
    except Exception as e:
        logging.error(f"An error occurred during wind data retrieval: {e}")
        return

    logging.info("Wind Data Retrieval Script Completed.")

if __name__ == "__main__":
    main()
