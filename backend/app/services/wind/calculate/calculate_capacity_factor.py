def calculate_capacity_factor(df, rated_power=10):
    """
    Calculate the capacity factor of the wind turbine.
    
    Parameters:
    - df (DataFrame): DataFrame containing the 'energy_kwh' column
    - rated_power (float): Rated power of the turbine in kW (default 10kW)
    
    Returns:
    - capacity_factor (float): Capacity factor as a percentage
    """
    # Calculate annual energy from monthly data
    annual_energy = df['energy_kwh'].sum() * 12  # Convert monthly to annual
    
    # Calculate theoretical maximum annual energy
    max_annual_energy = rated_power * 8760  # 8760 hours in a year
    
    # Calculate capacity factor
    capacity_factor = (annual_energy / max_annual_energy) * 100
    
    # Sanity check - cap at realistic maximum
    MAX_CAPACITY_FACTOR = 35.0
    return min(capacity_factor, MAX_CAPACITY_FACTOR)

def calculate_wind_cost_savings(total_energy_kwh: float, energy_price: float) -> float:
    """
    Calculate annual cost savings from wind energy.
    
    Parameters:
    - total_energy_kwh (float): Annual energy production in kWh
    - energy_price (float): Energy price in USD/kWh (typically 0.10-0.15)
    
    Returns:
    - annual_savings (float): Annual cost savings in USD
    """
    # Validate energy price is in reasonable range
    MIN_RATE = 0.08
    MAX_RATE = 0.20
    validated_rate = min(max(energy_price, MIN_RATE), MAX_RATE)
    
    return total_energy_kwh * validated_rate