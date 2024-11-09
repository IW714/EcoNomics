import cdsapi
import logging
import os

def setup_logging():
    """
    Sets up logging configuration.
    """
    logging.basicConfig(
        filename='fetch_era5_data.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def get_bounding_box(lat, lon, buffer_deg=0.25):
    """
    Calculate a bounding box around the given latitude and longitude.
    """
    north = lat + buffer_deg
    south = lat - buffer_deg
    east = lon + buffer_deg
    west = lon - buffer_deg

    # Ensure coordinates are within valid ranges
    north = min(north, 90)
    south = max(south, -90)
    east = min(east, 180)
    west = max(west, -180)

    return [north, west, south, east]

def fetch_data(lat, lon, buffer_deg, year, month, output_dir='era5_data'):
    """
    Fetch ERA5 data using the CDS API and save it as a NetCDF file.
    """
    c = cdsapi.Client()

    # Calculate bounding box
    area = get_bounding_box(lat, lon, buffer_deg)
    logging.info(f"Bounding Box: North={area[0]}, West={area[1]}, South={area[2]}, East={area[3]}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file name
    output_file = os.path.join(output_dir, f'era5_{year}_{month}.nc')

    # Check if file already exists to avoid redundant downloads
    if os.path.exists(output_file):
        logging.info(f"Data for {year}-{month} already exists at '{output_file}'. Skipping download.")
        return

    try:
        logging.info(f"Starting data retrieval for {year}-{month}...")
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
                'day': [
                    '01', '02', '03', '04',
                    '05', '06', '07', '08',
                    '09', '10', '11', '12',
                    '13', '14', '15', '16',
                    '17', '18', '19', '20',
                    '21', '22', '23', '24',
                    '25', '26', '27', '28',
                    '29', '30', '31',
                ],
                'time': [
                    '00:00', '06:00', '12:00', '18:00',
                ],
                'area': area,  # [North, West, South, East]
                'format': 'netcdf',
            },
            output_file)
        logging.info(f"Data retrieval successful. File saved as '{output_file}'.")
    except Exception as e:
        logging.error(f"Data retrieval failed: {e}")
        raise

def main():
    setup_logging()
    logging.info("ERA5 Data Retrieval Script Started.")

    # User inputs
    try:
        lat = float(input("Enter latitude (e.g., 51.626): "))
        lon = float(input("Enter longitude (e.g., 1.496): "))
        buffer_deg_input = input("Enter buffer in degrees (default 0.25): ")
        buffer_deg = float(buffer_deg_input) if buffer_deg_input else 0.25
        year = input("Enter year (e.g., 2019): ")
        month = input("Enter month (e.g., 01 for January): ")

        # Validate month
        if month not in [f"{i:02d}" for i in range(1, 13)]:
            logging.error("Invalid month entered. Please enter a value between 01 and 12.")
            return

    except ValueError as ve:
        logging.error(f"Invalid input: {ve}")
        return

    fetch_data(lat, lon, buffer_deg, year, month)

    logging.info("ERA5 Data Retrieval Script Completed.")

if __name__ == "__main__":
    main()
