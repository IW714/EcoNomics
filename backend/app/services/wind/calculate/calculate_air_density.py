import sys
import xarray as xr
import pandas as pd
import os
import numpy as np

def calculate_air_density(temperature, pressure_pa, dewpoint):
    """
    Calculate air density based on temperature (K), pressure (Pa), and dewpoint (K).
    """
    R_d = 287.05    # J/(kg·K) for dry air
    R_v = 461.495   # J/(kg·K) for water vapor
    T_celsius = dewpoint - 273.15  # Dewpoint in Celsius

    e_s_pa = 6.112 * np.exp((17.67 * T_celsius) / (T_celsius + 243.5)) * 100  # Convert hPa to Pa
    rho = ((pressure_pa - e_s_pa) / (R_d * temperature)) + (e_s_pa / (R_v * temperature))
    return rho

def calculate_air_density_from_nc(nc_file='data/era5.nc', output_csv='data/air_density_january_2019.csv'):
    """
    Calculate air density from ERA5 NetCDF data and save it to a CSV file.

    Parameters:
    - nc_file (str): Path to the ERA5 NetCDF file.
    - output_csv (str): Path to save the air density CSV file.
    """
    if not os.path.exists(nc_file):
        print(f"Error: NetCDF file '{nc_file}' not found.")
        raise FileNotFoundError(f"NetCDF file '{nc_file}' not found.")

    try:
        ds = xr.open_dataset(nc_file)
    except Exception as e:
        print(f"Error: Failed to load the NetCDF file: {e}")
        raise

    try:
        # Update 'time' dimension to 'valid_time' if necessary
        time_var = 'valid_time' if 'valid_time' in ds.dims else 'time'

        # Extract relevant data using the detected time variable
        times = ds[time_var].values
        temp_k = ds['t2m'].mean(dim=('latitude', 'longitude')).values
        dewpoint_k = ds['d2m'].mean(dim=('latitude', 'longitude')).values
        pressure_pa = ds['sp'].mean(dim=('latitude', 'longitude')).values
    except KeyError as e:
        print(f"Error: Variable '{e}' not found in the dataset.")
        raise
    except Exception as e:
        print(f"Error: An unexpected error occurred while extracting variables: {e}")
        raise

    air_density = calculate_air_density(temp_k, pressure_pa, dewpoint_k)

    df_air_density = pd.DataFrame({
        'datetime': pd.to_datetime(times),
        'air_density': air_density
    })

    try:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)  # Ensure the data directory exists
        df_air_density.to_csv(output_csv, index=False)
        print(f"Air density data successfully saved to '{output_csv}'.")
    except Exception as e:
        print(f"Failed to save air density data to CSV: {e}")
        raise

def main():
    nc_file = 'data/era5.nc'
    output_csv = 'data/air_density_january_2019.csv'
    calculate_air_density_from_nc(nc_file, output_csv)
    print("Air Density Calculation Script Completed.")

if __name__ == "__main__":
    main()
