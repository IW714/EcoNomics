def calculate_annual_wind_energy(total_energy_kwh: float) -> float:
    """
    Converts monthly energy to annual energy by multiplying by 12.
    
    :param total_energy_kwh: Monthly energy output from wind turbine (kWh)
    :return: Annualized energy in kWh
    """
    return total_energy_kwh * 12

def calculate_wind_cost_savings(total_energy_kwh: float, energy_price: float) -> float:
    """
    Calculates the annual cost savings based on wind energy production and energy price.

    :param total_energy_kwh: Monthly energy output from wind turbine (kWh)
    :param energy_price: Energy price in USD/kWh
    :return: Annual cost savings in USD
    """
    annual_energy = calculate_annual_wind_energy(total_energy_kwh)
    return annual_energy * energy_price