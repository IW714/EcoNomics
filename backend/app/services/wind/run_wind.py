import os
import subprocess
import argparse
import math

# Base directory for the scripts
base_dir = "/Users/westonvoglesonger/Projects/EcoNomics/backend/app/services/wind/"
location_file = os.path.join(base_dir, "last_location.txt")
data_dir = os.path.join(base_dir, "data/")
distance_threshold_km = 50  # Distance threshold in km

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth (specified in decimal degrees)"""
    R = 6371  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def load_last_location():
    if os.path.exists(location_file):
        with open(location_file, "r") as file:
            lat, lon = map(float, file.readline().split(","))
            return lat, lon
    return None, None

def save_current_location(lat, lon):
    with open(location_file, "w") as file:
        file.write(f"{lat},{lon}")

def check_location_change(lat, lon):
    last_lat, last_lon = load_last_location()
    if last_lat is None or last_lon is None:
        return True  # No previous location, treat as changed
    distance = haversine(last_lat, last_lon, lat, lon)
    return distance > distance_threshold_km

def delete_data_files():
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        os.remove(file_path)
    print("Existing data files deleted due to location change.")

def run_script(script_name, description, args):
    print(f"Running {description}...")
    script_path = os.path.join(base_dir, script_name)
    try:
        subprocess.run(["python", script_path] + args, check=True)
        print(f"{description} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred in {description}: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="Run wind data processing scripts with specified parameters.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude of the location")
    parser.add_argument("--lon", type=float, required=True, help="Longitude of the location")
    parser.add_argument("--height", type=int, required=True, help="Height above ground level in meters")
    parser.add_argument("--date_from", type=str, required=True, help="Start date in 'YYYY-MM-DD' format")
    parser.add_argument("--date_to", type=str, required=True, help="End date in 'YYYY-MM-DD' format")

    args = parser.parse_args()

    # Check for significant location change
    if check_location_change(args.lat, args.lon):
        delete_data_files()  # Delete old data if location changed
        save_current_location(args.lat, args.lon)  # Update location file

    # Convert args to a list of strings to pass to subprocess
    script_args = [
        str(args.lat),
        str(args.lon),
        str(args.height),
        args.date_from,
        args.date_to
    ]

    # List of scripts to run in order with descriptions
    scripts = [
        ("fetch/fetch_era5_data.py", "ERA5 Data Retrieval Script"),
        ("calculate/calculate_air_density.py", "Air Density Calculation Script"),
        ("fetch/fetch_wind_data.py", "Wind Data Retrieval Script"),
        ("calculate/merge_and_calculate_power.py", "Power and Energy Calculation Script"),
        ("calculate/calculate_capacity_factor.py", "Capacity Factor Calculation Script")
    ]

    # Execute each script in the list
    for script_name, description in scripts:
        script_path = os.path.join(base_dir, script_name)
        if os.path.exists(script_path):
            run_script(script_name, description, script_args)
        else:
            print(f"Script '{script_name}' not found at {script_path}. Skipping {description}.\n")

    print("All scripts have been executed.")

if __name__ == "__main__":
    main()
