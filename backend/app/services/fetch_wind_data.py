# fetch_wind_data.py

import requests
import pandas as pd
import logging
import os
from datetime import datetime

def setup_logging():
    """
    Sets up logging configuration.
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
    """
    url = "http://windatlas.xyz/api/wind/"  # Replace with the actual Wind Atlas API endpoint
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

        # Save the response content to CSV
        with open(output_file, 'w') as file:
            file.write(response.text)
        logging.info(f"Wind data successfully saved to '{output_file}'.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve wind data: {e}")
        raise

def main():
    setup_logging()
    logging.info("Wind Data Retrieval Script Started.")

    # User inputs
    try:
        lat = 51.626
        lon = 1.496
        height = 100
        date_from = 2019-01-01
        date_to = 2019-01-31
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
    output_file = f'wind_data_{date_from}_to_{date_to}.csv'

    # Check if file already exists to prevent redundant downloads
    if os.path.exists(output_file):
        logging.info(f"Wind data for {date_from} to {date_to} already exists at '{output_file}'. Skipping download.")
        return

    # Fetch wind data
    try:
        fetch_wind_data(lat, lon, height, date_from, date_to, output_file)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return

    logging.info("Wind Data Retrieval Script Completed.")

if __name__ == "__main__":
    main()
