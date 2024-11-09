# merge_and_calculate_power.py

import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

def setup_logging():
    """
    Sets up logging configuration.
    """
    logging.basicConfig(
        filename='merge_and_calculate_power.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def apply_power_curve(wind_speed, air_density, rotor_radius=50, efficiency=0.4, rated_power=2000):
    """
    Calculate power output in kW considering air density.
    """
    swept_area = 3.1416 * rotor_radius**2  # m²
    power_available = 0.5 * air_density * swept_area * (wind_speed ** 3)  # W
    power = power_available * efficiency / 1000  # kW

    if wind_speed < 3:
        return 0
    elif 3 <= wind_speed < 15:
        return power
    elif 15 <= wind_speed < 25:
        return rated_power
    else:
        return 0

def main():
    setup_logging()
    logging.info("Merging and Power Calculation Script Started.")

    # Define file paths
    wind_file = 'wind_data_2019-01-01_to_2019-01-31.csv'  # Update this line with your actual wind data file name
    air_density_file = 'air_density_january_2019.csv'
    output_file = 'merged_power_data.csv'

    # Check if files exist
    if not os.path.exists(wind_file):
        logging.error(f"Wind data file '{wind_file}' not found.")
        return
    if not os.path.exists(air_density_file):
        logging.error(f"Air density data file '{air_density_file}' not found.")
        return

    # Load wind data
    try:
        df_wind = pd.read_csv(wind_file, parse_dates=['datetime'])
        logging.info(f"Wind data loaded from '{wind_file}'.")
    except Exception as e:
        logging.error(f"Error loading wind data: {e}")
        return

    # Load air density data
    try:
        df_air = pd.read_csv(air_density_file, parse_dates=['datetime'])
        logging.info(f"Air density data loaded from '{air_density_file}'.")
    except Exception as e:
        logging.error(f"Error loading air density data: {e}")
        return

    # Merge on datetime
    df_merged = pd.merge(df_wind, df_air, on='datetime', how='left')
    logging.info("Data merged successfully.")

    # Forward fill any missing air density values
    df_merged['air_density'].fillna(method='ffill', inplace=True)
    logging.info("Missing air density values forward filled.")

    # Calculate power output
    df_merged['power_kw'] = df_merged.apply(
        lambda row: apply_power_curve(row['wind_speed'], row['air_density']),
        axis=1
    )
    logging.info("Power output calculated.")

    # Calculate energy generated (assuming hourly data)
    df_merged['energy_kwh'] = df_merged['power_kw']  # 1 hour intervals

    # Save merged data
    df_merged.to_csv(output_file, index=False)
    logging.info(f"Merged power data saved to '{output_file}'.")

    # Plot wind speed and power output
    plt.figure(figsize=(12, 6))
    plt.plot(df_merged['datetime'], df_merged['wind_speed'], label='Wind Speed (m/s)', color='blue', linewidth=1)
    plt.plot(df_merged['datetime'], df_merged['power_kw'], label='Power Output (kW)', color='green', linewidth=1)
    plt.title("Wind Speed and Power Output Over Time")
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s) / Power Output (kW)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    logging.info("Plot generated successfully.")

    # Calculate total energy generated
    total_energy_kwh = df_merged['energy_kwh'].sum()
    print(f"Total Energy Generated: {total_energy_kwh:.2f} kWh")
    logging.info(f"Total Energy Generated: {total_energy_kwh:.2f} kWh")

    logging.info("Merging and Power Calculation Script Completed.")

if __name__ == "__main__":
    main()
