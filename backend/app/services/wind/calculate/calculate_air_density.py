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

    e_s_pa = 6.112 * np.exp((17.67 * T_celsius) / (T_celsius + 243.5)) * 100
    rho = ((pressure_pa - e_s_pa) / (R_d * temperature)) + (e_s_pa / (R_v * temperature))
    return rho

def main():
    nc_file = 'data/era5.nc'

    if not os.path.exists(nc_file):
        print(f"Error: NetCDF file '{nc_file}' not found.")
        return

    try:
        ds = xr.open_dataset(nc_file)
    except Exception as e:
        print(f"Error: Failed to load the NetCDF file: {e}")
        return

    try:
        # Update 'time' dimension to 'valid_time' as needed
        time_var = 'valid_time' if 'valid_time' in ds.dims else 'time'

        # Extract relevant data using the detected time variable
        times = ds[time_var].values
        temp_k = ds['t2m'].mean(dim=('latitude', 'longitude')).values
        dewpoint_k = ds['d2m'].mean(dim=('latitude', 'longitude')).values
        pressure_pa = ds['sp'].mean(dim=('latitude', 'longitude')).values
    except KeyError as e:
        print(f"Error: Variable '{e}' not found in the dataset.")
        return
    except Exception as e:
        print(f"Error: An unexpected error occurred while extracting variables: {e}")
        return

    air_density = calculate_air_density(temp_k, pressure_pa, dewpoint_k)

    df_air_density = pd.DataFrame({
        'datetime': pd.to_datetime(times),
        'air_density': air_density
    })

    output_csv = 'data/air_density_january_2019.csv'
    df_air_density.to_csv(output_csv, index=False)
    print(f"Air density data successfully saved to '{output_csv}'.")

if __name__ == "__main__":
    main()
