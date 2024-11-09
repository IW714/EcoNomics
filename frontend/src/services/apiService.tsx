import { SolarAssessmentResponse, WindDataResponse } from "@/models/types";

export const calculateSolarPotential = async (
  payload: any
): Promise<SolarAssessmentResponse> => {
  const response = await fetch("http://127.0.0.1:8000/calculate_solar_potential", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to calculate solar potential");
  }

  return response.json();
};

export const processWindData = async (
  latitude: number,
  longitude: number,
  height: number = 100,
  dateFrom: string = "2019-01-01",
  dateTo: string = "2019-01-31"
): Promise<WindDataResponse> => {
  const response = await fetch("http://127.0.0.1:8000/process_wind_data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ lat: latitude, lon: longitude, height, date_from: dateFrom, date_to: dateTo }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch wind data");
  }

  return response.json();
};
