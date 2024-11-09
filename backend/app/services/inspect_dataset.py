# inspect_dataset.py

import xarray as xr

def main():
    # Replace with your actual NetCDF file path
    nc_file = 'era5_data/era5_2019_01.nc'
    
    try:
        ds = xr.open_dataset(nc_file)
        print(ds)
    except FileNotFoundError:
        print(f"Error: File '{nc_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
