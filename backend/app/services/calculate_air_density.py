# calculate_air_density.py

import xarray as xr
import pandas as pd
import logging
import os

def setup_logging():
    """
    Sets up logging configuration.
    """
    logging.basicConfig(
        filename='calculate_air_density.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def calculate_air_density(temperature, pressure, dewpoint):
    """
    Calculate air density using temperature (K), pressure (hPa), and dewpoint (K).
    """
    # Constants
    R_d = 287.05  # J/(kg·K), specific gas constant for dry air
    R_v = 461.495  # J/(kg·K), specific gas constant for water vapor

    # Saturation vapor pressure (e_s) using dewpoint temperature (Tetens formula)
    e_s = 6.112 * 10**((7.5 * (dewpoint - 273.15)) / (dewpoint - 35.85))

    # Actual vapor pressure (e) assuming dewpoint = actual vapor pressure
    e = e_s

    # Air density calculation (kg/m³)
    rho = ((pressure * 100) - (e * 100)) / (R_d * temperature) + (e * 100) / (R_v * temperature)
    return rho

def main():
    setup_logging()
    logging.info("Air Density Calculation Script Started.")

    # Define the path to the NetCDF file
    nc_file = 'era5_data/era5_2019_01.nc'  # Update based on your inputs

    # Check if the NetCDF file exists
    if not os.path.exists(nc_file):
        logging.error(f"NetCDF file '{nc_file}' not found. Please ensure data retrieval was successful.")
        return

    try:
        # Open the NetCDF dataset
        ds = xr.open_dataset(nc_file)
        logging.info(f"Successfully loaded '{nc_file}'.")
    except Exception as e:
        logging.error(f"An error occurred while loading the NetCDF file: {e}")
        return

    # Inspect available variables
    available_vars = list(ds.variables)
    logging.info(f"Available variables in the dataset: {available_vars}")

    # Extract variables
    try:
        # Use 'valid_time' instead of 'time' if 'time' does not exist
        if 'valid_time' in ds.coords:
            times = ds['valid_time'].values
            logging.info("Using 'valid_time' as the time coordinate.")
        elif 'time' in ds.coords:
            times = ds['time'].values
            logging.info("Using 'time' as the time coordinate.")
        else:
            logging.error("No time coordinate ('time' or 'valid_time') found in the dataset.")
            return

        temp_k = ds['t2m'].values  # 2m temperature in Kelvin
        dewpoint_k = ds['d2m'].values  # 2m dewpoint temperature in Kelvin
        pressure_hpa = ds['sp'].values  # Surface pressure in hPa
        logging.info("Successfully extracted variables from the dataset.")
    except KeyError as e:
        logging.error(f"Variable {e} not found in the dataset.")
        return
    except Exception as e:
        logging.error(f"An error occurred while extracting variables: {e}")
        return

    # Calculate air density for each timestamp
    logging.info("Calculating air density...")
    air_density = []
    for i in range(len(times)):
        rho = calculate_air_density(temp_k[i], pressure_hpa[i], dewpoint_k[i])
        air_density.append(rho)

    # Create a DataFrame
    df_air_density = pd.DataFrame({
        'datetime': pd.to_datetime(times),
        'air_density': air_density
    })

    # Save to CSV
    output_csv = 'air_density_january_2019.csv'
    df_air_density.to_csv(output_csv, index=False)
    logging.info(f"Air density data saved to '{output_csv}'.")

    logging.info("Air Density Calculation Script Completed.")

if __name__ == "__main__":
    main()
