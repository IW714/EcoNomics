import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { SolarAssessmentResponse, WindDataResponse } from "@/models/types";
import { calculateSolarPotential, processWindData, getCoordinates } from "@/services/apiService";
import { useState } from "react";

const HomePage = () => {
  const [longitude, setLongitude] = useState("");
  const [latitude, setLatitude] = useState("");
  const [cityName, setCityName] = useState("");
  const [solarResult, setSolarResult] = useState<SolarAssessmentResponse | null>(null);
  const [windResult, setWindResult] = useState<WindDataResponse | null>(null);
  const [solarError, setSolarError] = useState("");
  const [windError, setWindError] = useState("");
  const [loading, setLoading] = useState(false);

  const validateCoordinates = (lat: number, lon: number): boolean => {
    return !isNaN(lat) && !isNaN(lon) && 
           lat >= -90 && lat <= 90 && 
           lon >= -180 && lon <= 180;
  };

  const getCoords = async () => {
    if (cityName.trim()) {
      try {
        const coords = await getCoordinates({ city_name: cityName.trim() });
        setLatitude(coords.latitude.toString());
        setLongitude(coords.longitude.toString());
        return coords;
      } catch (err) {
        console.error("Failed to fetch coordinates:", err);
        throw new Error("Failed to get coordinates for the provided city name");
      }
    }
    return null;
  };

  const handleSolarSubmit = async () => {
    setSolarError("");
    setLoading(true);

    try {
      let lat = Number(latitude);
      let lon = Number(longitude);

      if (cityName.trim()) {
        const coords = await getCoords();
        if (coords) {
          lat = coords.latitude;
          lon = coords.longitude;
        }
      }

      if (!validateCoordinates(lat, lon)) {
        throw new Error("Please enter valid coordinates or a city name");
      }

      const data = await calculateSolarPotential({ 
        latitude: lat, 
        longitude: lon 
      });
      setSolarResult(data);
    } catch (err) {
      setSolarError(err instanceof Error ? err.message : "Failed to calculate solar potential");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleWindSubmit = async () => {
    setWindError("");
    setLoading(true);
    setWindResult(null);
    
    try {
      let lat = Number(latitude);
      let lon = Number(longitude);
      
      if (cityName.trim()) {
        const coords = await getCoords();
        if (coords) {
          lat = coords.latitude;
          lon = coords.longitude;
        }
      }

      if (!validateCoordinates(lat, lon)) {
        throw new Error("Please enter valid coordinates or a city name");
      }

      const data = await processWindData(
        lat,
        lon,
        100,
        "2019-01-01",
        "2019-01-31"
      );
      
      setWindResult(data);
    } catch (err) {
      if (err instanceof Error) {
        setWindError(err.message);
      } else {
        setWindError("Failed to fetch wind data");
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Renewable Energy Assessment</CardTitle>
          <CardDescription>
            Enter a city name or coordinates to calculate solar and wind energy potential
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">City Name</label>
              <Input
                type="text"
                placeholder="Enter city name (e.g., New York)"
                value={cityName}
                onChange={(e) => setCityName(e.target.value)}
                className="w-full"
              />
            </div>

            <div className="text-center text-sm text-gray-500">- OR -</div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Latitude</label>
                <Input
                  type="number"
                  placeholder="Enter latitude"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  step="any"
                  min="-90"
                  max="90"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Longitude</label>
                <Input
                  type="number"
                  placeholder="Enter longitude"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  step="any"
                  min="-180"
                  max="180"
                />
              </div>
            </div>
          </div>
        </CardContent>
        
        <CardFooter className="flex flex-col space-y-4">
          <div className="flex space-x-4 w-full">
            <Button 
              onClick={handleSolarSubmit} 
              disabled={loading}
              className="flex-1"
            >
              {loading ? "Calculating..." : "Calculate Solar Potential"}
            </Button>
            <Button 
              onClick={handleWindSubmit} 
              disabled={loading}
              className="flex-1"
            >
              {loading ? "Calculating..." : "Calculate Wind Potential"}
            </Button>
          </div>

          {(solarError || windError) && (
            <div className="w-full p-4 bg-red-50 border border-red-200 rounded-md">
              {solarError && <p className="text-red-600">{solarError}</p>}
              {windError && <p className="text-red-600">{windError}</p>}
            </div>
          )}
        </CardFooter>

        {(solarResult || windResult) && (
          <div className="p-6 border-t border-gray-200">
            {solarResult && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-4">Solar Assessment Results</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium text-gray-600">Annual AC Output</p>
                    <p className="text-lg">{solarResult.ac_annual.toFixed(2)} kWh</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium text-gray-600">Solar Radiation</p>
                    <p className="text-lg">{solarResult.solrad_annual.toFixed(2)} kWh/m²/day</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium text-gray-600">Capacity Factor</p>
                    <p className="text-lg">{(solarResult.capacity_factor * 100).toFixed(1)}%</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium text-gray-600">Panel Area</p>
                    <p className="text-lg">{solarResult.panel_area.toFixed(2)} m²</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium text-gray-600">Annual Savings</p>
                    <p className="text-lg">${solarResult.annual_cost_savings.toFixed(2)}</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium text-gray-600">ROI Period</p>
                    <p className="text-lg">{solarResult.roi_years.toFixed(1)} years</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-md col-span-2">
                    <p className="text-sm font-medium text-gray-600">CO₂ Reduction</p>
                    <p className="text-lg">{solarResult.co2_reduction.toFixed(2)} kg/year</p>
                  </div>
                </div>
              </div>
            )}

                {windResult && (
                <div>
                    <h3 className="text-lg font-semibold mb-4">Wind Assessment Results</h3>
                    <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm font-medium text-gray-600">Annual Energy Output</p>
                        <p className="text-lg">{windResult.total_energy_kwh.toFixed(2)} kWh</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm font-medium text-gray-600">Capacity Factor</p>
                        <p className="text-lg">{windResult.capacity_factor_percentage.toFixed(1)}%</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm font-medium text-gray-600">Annual Savings</p>
                        <p className="text-lg">${windResult.cost_savings.toFixed(2)}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm font-medium text-gray-600">Payback Period</p>
                        <p className="text-lg">{(30000 / windResult.cost_savings).toFixed(1)} years</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md col-span-2">
                        <p className="text-sm font-medium text-gray-600">CO₂ Reduction</p>
                        <p className="text-lg">{(windResult.total_energy_kwh * 0.131).toFixed(2)} kg/year</p>
                    </div>
                    </div>
                </div>
                )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default HomePage;