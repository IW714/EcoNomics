import pandas as pd
import numpy as np
import os

def apply_power_curve(wind_speed, air_density, rotor_radius=50, rated_power=2000, Cp=0.4):
    """
    Calculate power output in kW based on wind speed and air density using a turbine power curve.

    Parameters:
    - wind_speed (float): Wind speed in meters per second (m/s).
    - air_density (float): Air density in kg/m³.
    - rotor_radius (float): Radius of the turbine rotor in meters.
    - rated_power (float): Rated power output of the turbine in kW.
    - Cp (float): Power coefficient representing turbine efficiency.

    Returns:
    - power (float): Calculated power output in kW.
    """
    # Define operational speed limits for the turbine
    cut_in_speed = 3    # Minimum wind speed for turbine operation (m/s)
    rated_speed = 15    # Wind speed at which rated power is achieved (m/s)
    cut_out_speed = 25  # Maximum wind speed before turbine shuts down (m/s)

    # Calculate the swept area of the rotor (A = π * r²)
    swept_area = np.pi * rotor_radius ** 2  # in square meters

    # Determine power output based on the turbine's power curve
    if wind_speed < cut_in_speed or wind_speed >= cut_out_speed:
        return 0  # No power generated outside operational speeds
    elif wind_speed < rated_speed:
        # Power scales cubically between cut-in and rated speeds
        power = 0.5 * air_density * swept_area * Cp * (wind_speed ** 3) / 1000  # Convert W to kW
        return min(power, rated_power)  # Limit to rated power
    else:
        return rated_power  # Rated power output above rated speed

def merge_and_calculate_power(wind_data_file, air_density_file, output_file):
    """
    Merge wind speed and use mean air density data, then calculate power and energy output.

    Parameters:
    - wind_data_file (str): Path to the CSV file containing wind speed data.
    - air_density_file (str): Path to the CSV file containing air density data.
    - output_file (str): Path to save the output CSV file with calculated power and energy.
    """
    # Load the wind data
    df_wind = pd.read_csv(wind_data_file, parse_dates=['datetime'])
    
    # Load air density data and calculate mean air density
    df_air_density = pd.read_csv(air_density_file, parse_dates=['datetime'])
    mean_air_density = df_air_density['air_density'].mean()
    print(f"Using mean air density: {mean_air_density:.4f} kg/m³")

    # Apply the power curve calculation using the mean air density for each row
    df_wind['power_kw'] = df_wind['wind_speed'].apply(
        lambda wind_speed: apply_power_curve(
            wind_speed=wind_speed,
            air_density=mean_air_density
        )
    )

    # Calculate energy generated per hour (kWh), assuming each row represents one hour
    df_wind['energy_kwh'] = df_wind['power_kw']  # kW * 1 hour = kWh

    # Save the data with calculated power and energy output to a new CSV file
    df_wind.to_csv(output_file, index=False)
    print(f"Data successfully saved to '{output_file}'.")

def calculate_total_energy(output_file):
    """
    Calculate the total energy generated from the merged data file.
    """
    df = pd.read_csv(output_file)
    # Sum the energy_kwh column to get the total energy generated over the period
    total_energy = df['energy_kwh'].sum()
    print(f"Total Energy Generated: {total_energy:.2f} kWh")

def main():
    # File paths for input wind and air density data, and output for merged results
    wind_data_file = 'data/wind_data.csv'
    air_density_file = 'data/air_density_january_2019.csv'
    output_file = 'data/merged_power_data.csv'

    # Check if the required input files exist
    if not os.path.exists(wind_data_file):
        print(f"Error: Wind data file '{wind_data_file}' not found.")
        return
    if not os.path.exists(air_density_file):
        print(f"Error: Air density file '{air_density_file}' not found.")
        return

    # Perform data merging and power calculation
    merge_and_calculate_power(wind_data_file, air_density_file, output_file)
    print("Merge and power calculation completed.")

    # Calculate and display the total energy generated
    calculate_total_energy(output_file)

if __name__ == "__main__":
    main()
