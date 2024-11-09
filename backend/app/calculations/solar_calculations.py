import logging

# Configure the logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def calculate_panel_area(dc_annual: float, solrad_annual: float, panel_efficiency: float) -> float:
    """
    Calculates the required panel area based on DC annual output, solar radiation, and panel efficiency.

    :param dc_annual: Annual DC output (kWhdc)
    :param solrad_annual: Average daily solar radiation (kWh/m²/day)
    :param panel_efficiency: Panel efficiency (e.g., 0.18 for 18%)
    :return: Required panel area in m²
    """
    # Convert solrad from kWh/m²/day to kWh/m²/year
    annual_solar_radiation = solrad_annual * 365  # kWh/m²/year
    logger.debug(f"Annual Solar Radiation: {annual_solar_radiation} kWh/m²/year")
    
    if annual_solar_radiation <= 0:
        raise ValueError("Annual solar radiation must be greater than 0.")
    
    panel_area = dc_annual / (annual_solar_radiation * panel_efficiency)
    logger.debug(f"Calculated Panel Area: {panel_area} m²")
    
    return panel_area

def calculate_cost_savings(ac_annual: float, energy_price: float) -> float:
    """
    Calculates the annual cost savings based on AC annual output and energy price.

    :param ac_annual: Annual AC output (kWhac)
    :param energy_price: Energy price in USD/kWh
    :return: Annual cost savings in USD
    """
    return ac_annual * energy_price

def calculate_roi(initial_cost: float, annual_savings: float) -> float:
    """
    Calculates the Return on Investment (ROI) in years.

    :param initial_cost: Initial installation cost (USD)
    :param annual_savings: Annual cost savings (USD)
    :return: ROI in years
    """
    if annual_savings <= 0:
        raise ValueError("Annual savings must be greater than 0.")
    return initial_cost / annual_savings

def calculate_co2_reduction(ac_annual: float, emission_factor: float) -> float:
    """
    Calculates the annual CO2 reduction.

    :param ac_annual: Annual AC output (kWhac)
    :param emission_factor: CO2 emission factor in kg CO2/kWh
    :return: Annual CO2 reduction in kg
    """
    return ac_annual * emission_factor  # in kg