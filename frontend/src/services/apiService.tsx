import { SolarAssessmentResponse, WindDataResponse } from "@/models/types";

const API_BASE_URL = "http://127.0.0.1:8000";

interface CoordinatesResponse {
  latitude: number;
  longitude: number;
}

const handleApiError = async (response: Response, errorMessage: string) => {
  try {
    const errorDetails = await response.text();
    const errorJson = JSON.parse(errorDetails);
    if (errorJson.detail === "No climate data found with dataset=nsrdb for location specified: lat=56.0 lon=1.4") {
      throw new Error("We currently don't have coverage at this location.");
    } else {
      throw new Error(errorJson.detail || errorMessage);
    }
  } catch (e) {
    if (e instanceof Error) {
      throw e;
    }
    throw new Error(errorMessage);
  }
};

export const getCoordinates = async (payload: { city_name: string }): Promise<CoordinatesResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/get_coordinates`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      await handleApiError(response, "Failed to fetch coordinates");
    }

    return await response.json();
  } catch (error) {
    console.error("Error in getCoordinates:", error);
    throw error instanceof Error ? error : new Error("Failed to fetch coordinates");
  }
};

export const calculateSolarPotential = async (
  payload: { latitude: number; longitude: number }
): Promise<SolarAssessmentResponse> => {
  try {
    if (!payload.latitude || !payload.longitude || 
        isNaN(payload.latitude) || isNaN(payload.longitude) ||
        payload.latitude < -90 || payload.latitude > 90 ||
        payload.longitude < -180 || payload.longitude > 180) {
      throw new Error("Invalid coordinates provided");
    }

    const response = await fetch(`${API_BASE_URL}/calculate_solar_potential`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      await handleApiError(response, "Failed to calculate solar potential");
    }

    return await response.json();
  } catch (error) {
    console.error("Error in calculateSolarPotential:", error);
    throw error instanceof Error ? error : new Error("Failed to calculate solar potential");
  }
};

export const processWindData = async (
  latitude: number,
  longitude: number,
  height: number = 100,
  dateFrom: string = "2019-01-01",
  dateTo: string = "2019-01-31"
): Promise<WindDataResponse> => {
  try {
    if (!latitude || !longitude || 
        isNaN(latitude) || isNaN(longitude) ||
        latitude < -90 || latitude > 90 ||
        longitude < -180 || longitude > 180) {
      throw new Error("Invalid coordinates provided");
    }

    const payload = {
      lat: latitude,
      lon: longitude,
      height,
      date_from: dateFrom,
      date_to: dateTo
    };

    const response = await fetch(`${API_BASE_URL}/process_wind_data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      try {
        const errorJson = JSON.parse(errorText);
        if (errorJson.detail === "We currently don't have coverage in this location.") {
          throw new Error("We currently don't have coverage at this location.");
        } else {
          throw new Error(errorJson.detail || "Failed to process wind data");
        }
      } catch (e) {
        if (e instanceof Error) {
          throw e;
        }
        throw new Error("Failed to process wind data");
      }
    }

    return await response.json();
  } catch (error) {
    console.error("Error in processWindData:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to process wind data");
  }
};