import requests
import pandas as pd
import matplotlib.pyplot as plt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_wind_data(lat, lon, height, date_from, date_to, format='csv', timeout=10):
    # Updated URL to use HTTP instead of HTTPS
    url = "http://windatlas.xyz/api/wind/"
    params = {
        'lat': lat,
        'lon': lon,
        'height': height,
        'date_from': date_from,
        'date_to': date_to,
        'format': format
    }

    # Setup retry strategy
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectTimeout:
        print(f"Connection to {url} timed out after {timeout} seconds.")
        raise
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        raise
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        raise

def save_wind_data(data, filename='wind_data.csv'):
    with open(filename, 'w') as file:
        file.write(data)

def load_wind_data(filename='wind_data.csv'):
    # Assuming the first line contains metadata, skip it
    df = pd.read_csv(filename, skiprows=1)
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

def apply_power_curve(wind_speed):
    """
    Simplified turbine power curve function.
    Replace this with the actual power curve of your wind turbine.
    """
    if wind_speed < 3:
        return 0  # Turbine does not produce power below cut-in speed
    elif 3 <= wind_speed <= 15:
        # Linear interpolation between cut-in and rated speed
        return ((wind_speed - 3) / (15 - 3)) * 2000  # Max power of 2000 kW at 15 m/s
    elif 15 < wind_speed <= 25:
        return 2000  # Constant power output at rated power
    else:
        return 0  # Turbine shuts down above cut-out speed

def calculate_power_output(df):
    df['power_kw'] = df['wind_speed'].apply(apply_power_curve)
    df['energy_kwh'] = df['power_kw']  # Since data is hourly, power in kW equals energy in kWh
    return df

def plot_wind_and_power(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['datetime'], df['wind_speed'], label='Wind Speed (m/s)', color='blue', linewidth=1)
    plt.plot(df['datetime'], df['power_kw'], label='Power Output (kW)', color='green', linewidth=1)
    plt.title("Wind Speed and Power Output Over Time")
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s) / Power Output (kW)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    # Parameters for the API call
    lat = 51.626       # Latitude
    lon = 1.496        # Longitude
    height = 100       # Height in meters
    date_from = '2019-01-01'  # Start date
    date_to = '2019-01-31'    # End date

    # Retrieve wind data from the API
    print("Retrieving wind data from the API...")
    try:
        data = get_wind_data(lat, lon, height, date_from, date_to)
        save_wind_data(data, 'wind_data.csv')
        print("Data saved to wind_data.csv")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve wind data: {e}")
        return

    # Load and process the data
    print("Loading and processing data...")
    try:
        df = load_wind_data('wind_data.csv')
        df = calculate_power_output(df)
    except Exception as e:
        print(f"Failed to process wind data: {e}")
        return

    # Calculate total energy generated
    total_energy_kwh = df['energy_kwh'].sum()
    print(f"Total Energy Generated: {total_energy_kwh:.2f} kWh")

    # Plot the results
    print("Plotting wind speed and power output...")
    try:
        plot_wind_and_power(df)
    except Exception as e:
        print(f"Failed to plot data: {e}")

if __name__ == "__main__":
    main()
