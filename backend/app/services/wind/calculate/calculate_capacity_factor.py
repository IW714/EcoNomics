import pandas as pd

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

def main():
    # Load the data from the merged CSV file which contains energy output data
    # The 'datetime' column is parsed as dates for any time-based calculations if needed
    df = pd.read_csv('data/merged_power_data.csv', parse_dates=['datetime'])

    # Define the rated power of the wind turbine (in kW)
    rated_power = 2000  # This is a 2 MW turbine

    # Calculate the capacity factor based on actual energy output and maximum possible output
    capacity_factor = calculate_capacity_factor(df, rated_power)

    # Print the capacity factor with two decimal precision
    print(f"Capacity Factor: {capacity_factor:.2f}%")

if __name__ == "__main__":
    main()
