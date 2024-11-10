import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { SolarAssessmentResponse, WindDataResponse } from "@/models/types";
import { calculateSolarPotential, processWindData, getCoordinates } from "@/services/apiService";
import ChatWidget from "./ChatWidget";

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
    return !isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
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

      const data = await calculateSolarPotential({ latitude: lat, longitude: lon });
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

      const data = await processWindData(lat, lon, 100, "2019-01-01", "2019-01-31");

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
    <div className="container mx-auto p-4 flex flex-col lg:flex-row gap-8 justify-center">
      
      {/* Chat Widget in the Top Left */}
      <div className="lg:w-2/3">
          <CardHeader>
            <CardTitle>Chat Assistance</CardTitle>
          </CardHeader>
          <CardContent>
            <ChatWidget />
          </CardContent>
      </div>

      {/* Renewable Energy Assessment */}
      <div className="lg:w-2/3">
        <Card className="w-full shadow-md rounded-lg">
          <CardHeader>
            <CardTitle>Renewable Energy Assessment</CardTitle>
            <CardDescription>
              Enter a city name or coordinates to calculate solar and wind energy potential.
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
              <Button onClick={handleSolarSubmit} disabled={loading} className="flex-1">
                {loading ? "Calculating..." : "Calculate Solar Potential"}
              </Button>
              <Button onClick={handleWindSubmit} disabled={loading} className="flex-1">
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

          {/* Display Results */}
          {(solarResult || windResult) && (
            <div className="p-6 border-t border-gray-200">
              {solarResult && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-4">Solar Assessment Results</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {/* Solar results here */}
                  </div>
                </div>
              )}

              {windResult && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Wind Assessment Results</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {/* Wind results here */}
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default HomePage;
