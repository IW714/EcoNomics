export interface ChatResponse {
  response: string;
  solar_assessment?: SolarAssessmentResponse;
  wind_assessment?: WindDataResponse;
}

export interface SolarAssessmentResponse {
  ac_annual: number;
  solrad_annual: number;
  capacity_factor: number;
  panel_area: number;
  annual_cost_savings: number;
  roi_years: number;
  co2_reduction: number;
}
  
export interface WindDataResponse {
  total_energy_kwh: number;
  capacity_factor_percentage: number;
  cost_savings: number; 
  message: string;
}

export interface CombinedAssessmentResponse {
  solar_assessment: SolarAssessmentResponse;
  wind_assessment: WindDataResponse;
}