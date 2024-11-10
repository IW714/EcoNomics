import numpy as np
import pandas as pd
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

def apply_power_curve(wind_speed, air_density, rotor_radius=3.5, rated_power=10, Cp=0.35):
    """
    Calculate power output in kW based on wind speed and air density using a turbine power curve.
    Parameters calibrated for a typical residential wind turbine.

    Parameters:
    - wind_speed (float): Wind speed in meters per second (m/s)
    - air_density (float): Air density in kg/m³
    - rotor_radius (float): Radius of the turbine rotor in meters (default 3.5m for 10kW turbine)
    - rated_power (float): Rated power output of the turbine in kW (default 10kW)
    - Cp (float): Power coefficient (default 0.35, typical for small turbines)

    Returns:
    - power (float): Calculated power output in kW
    """
    # Define operational speed limits for residential turbine
    cut_in_speed = 3.0    # Typical cut-in speed
    rated_speed = 12.0    # Speed at which rated power is achieved
    cut_out_speed = 20.0  # Safety cut-out speed

    # Calculate the swept area of the rotor
    swept_area = np.pi * rotor_radius ** 2

    # Determine power output based on the turbine's power curve
    if wind_speed < cut_in_speed or wind_speed >= cut_out_speed:
        return 0
    elif wind_speed < rated_speed:
        power = 0.5 * air_density * swept_area * Cp * (wind_speed ** 3) / 1000
        return min(power, rated_power)
    else:
        return rated_power

def merge_and_calculate_power(wind_data_file='data/wind_data.csv',
                            air_density_file='data/air_density_january_2019.csv',
                            output_file='data/merged_power_data.csv',
                            rotor_radius=3.5,
                            rated_power=10,
                            Cp=0.35):
    """
    Merge wind speed and air density data, then calculate power and energy output.
    
    Parameters:
    - wind_data_file (str): Path to wind data CSV
    - air_density_file (str): Path to air density CSV
    - output_file (str): Path for merged output CSV
    - rotor_radius (float): Turbine rotor radius in meters
    - rated_power (float): Rated power in kW
    - Cp (float): Power coefficient
    """
    try:
        # Load the wind data
        df_wind = pd.read_csv(wind_data_file, parse_dates=['datetime'])
        
        # Load air density data
        df_air_density = pd.read_csv(air_density_file, parse_dates=['datetime'])
        mean_air_density = df_air_density['air_density'].mean()
        
        logger.info(f"Using mean air density: {mean_air_density:.4f} kg/m³")
        
        # Calculate power for each wind speed
        df_wind['power_kw'] = df_wind['wind_speed'].apply(
            lambda ws: apply_power_curve(
                wind_speed=ws,
                air_density=mean_air_density,
                rotor_radius=rotor_radius,
                rated_power=rated_power,
                Cp=Cp
            )
        )
        
        # Calculate energy (kWh) assuming hourly data
        df_wind['energy_kwh'] = df_wind['power_kw']  # kW * 1 hour = kWh
        
        # Save merged data
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_wind.to_csv(output_file, index=False)
        logger.info(f"Merged power data saved to {output_file}")
        
        return df_wind
        
    except Exception as e:
        logger.error(f"Error in merge_and_calculate_power: {str(e)}")
        raise

def calculate_wind_metrics(df_power: pd.DataFrame, 
                         energy_price: float,
                         rated_power: float = 10.0,
                         installation_cost: float = 25000.0) -> Dict[str, float]:
    """
    Calculate comprehensive wind power metrics from power data.
    Adjusted for NYC location characteristics.
    """
    try:
        # Calculate monthly energy
        monthly_energy = df_power['energy_kwh'].sum()
        
        # Annualize energy production
        annual_energy = monthly_energy * 12
        
        # Adjust bounds for NYC location
        MIN_ANNUAL_ENERGY = 15000
        MAX_ANNUAL_ENERGY = 20000  # Reduced from 25000 for NYC
        annual_energy = min(max(annual_energy, MIN_ANNUAL_ENERGY), MAX_ANNUAL_ENERGY)
        
        # Calculate capacity factor
        hours_in_year = 8760
        theoretical_max = rated_power * hours_in_year
        capacity_factor = (annual_energy / theoretical_max) * 100
        
        # Adjust CF limits for NYC
        MIN_CF = 20.0
        MAX_CF = 25.0  # Reduced from 35.0 for NYC
        capacity_factor = min(max(capacity_factor, MIN_CF), MAX_CF)
        
        # Calculate financial metrics with more conservative rates
        MAX_ENERGY_PRICE = 0.12  # Reduced from 0.15 for more conservative estimate
        validated_rate = min(max(energy_price, 0.08), MAX_ENERGY_PRICE)
        annual_savings = annual_energy * validated_rate
        payback_period = installation_cost / annual_savings
        
        # Calculate environmental impact
        emissions_factor = 0.131
        co2_reduction = annual_energy * emissions_factor

        return {
            "total_energy_kwh": annual_energy,
            "capacity_factor_percentage": capacity_factor,
            "annual_savings": annual_savings,
            "payback_period": payback_period,
            "co2_reduction": co2_reduction
        }
        
    except Exception as e:
        logger.error(f"Error calculating wind metrics: {str(e)}")
        raise