import sys
import pandas as pd
import os

def calculate_capacity_factor(df, rated_power):
    """
    Calculate the capacity factor of the wind turbine.

    Parameters:
    - df (DataFrame): DataFrame containing the 'energy_kwh' column.
    - rated_power (float): Rated power of the turbine in kW.

    Returns:
    - capacity_factor (float): Capacity factor as a percentage.
    """
    # Calculate the total number of hours represented by the data
    # Assumes each row in the DataFrame represents one hour
    total_hours = df.shape[0]

    # Calculate the maximum possible energy output if the turbine operated
    # at full rated power for the entire period (total_hours)
    total_possible_energy = rated_power * total_hours  # in kWh

    # Calculate the actual energy generated over the period by summing the 'energy_kwh' column
    actual_energy_generated = df['energy_kwh'].sum()

    # Calculate the capacity factor as a percentage
    # Capacity Factor = (Actual Energy Generated / Maximum Possible Energy) * 100
    capacity_factor = (actual_energy_generated / total_possible_energy) * 100
    return capacity_factor

def calculate_capacity_factor_from_csv(merged_power_file='data/merged_power_data.csv',
                                      rated_power=2000,
                                      output_file='data/capacity_factor.txt'):
    """
    Calculate the capacity factor from the merged power data and save it to a file.

    Parameters:
    - merged_power_file (str): Path to the CSV file containing merged power data.
    - rated_power (float): Rated power of the turbine in kW.
    - output_file (str): Path to save the capacity factor.
    """
    if not os.path.exists(merged_power_file):
        print(f"Error: Merged power data file '{merged_power_file}' not found.")
        raise FileNotFoundError(f"Merged power data file '{merged_power_file}' not found.")

    try:
        df = pd.read_csv(merged_power_file, parse_dates=['datetime'])
    except Exception as e:
        print(f"Error: Failed to read merged power data CSV: {e}")
        raise

    capacity_factor = calculate_capacity_factor(df, rated_power)
    print(f"Capacity Factor: {capacity_factor:.2f}%")

    # Save the capacity factor to a file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(f"Capacity Factor: {capacity_factor:.2f}%\n")
        print(f"Capacity factor successfully saved to '{output_file}'.")
    except Exception as e:
        print(f"Failed to save capacity factor to file: {e}")
        raise

    return capacity_factor  # Ensure the function returns the calculated value

def main():
    merged_power_file = 'data/merged_power_data.csv'
    rated_power = 2000  # kW, adjust as needed
    output_file = 'data/capacity_factor.txt'

    calculate_capacity_factor_from_csv(merged_power_file, rated_power, output_file)
    print("Capacity Factor Calculation Script Completed.")

if __name__ == "__main__":
    main()
