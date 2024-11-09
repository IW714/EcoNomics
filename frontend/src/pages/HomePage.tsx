import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { SolarAssessmentResponse, WindDataResponse } from "@/models/types";
import { calculateSolarPotential, processWindData } from "@/services/apiService";
import { useState } from "react";

const HomePage = () => {
  const [longitude, setLongitude] = useState("");
  const [latitude, setLatitude] = useState("");
  const [solarResult, setSolarResult] = useState<SolarAssessmentResponse | null>(null);
  const [windResult, setWindResult] = useState<WindDataResponse | null>(null);
  const [solarError, setSolarError] = useState("");
  const [windError, setWindError] = useState("");

  // Solar data submission
  const handleSolarSubmit = async () => {
    setSolarError("");
    try {
      const data = await calculateSolarPotential({ latitude: Number(latitude), longitude: Number(longitude) });
      setSolarResult(data);
    } catch (err) {
      setSolarError("Failed to calculate solar potential");
      console.error(err);
    }
  };

  // Wind data submission
  const handleWindSubmit = async () => {
    setWindError("");
    try {
      const data = await processWindData(Number(latitude), Number(longitude));
      setWindResult(data);
    } catch (err) {
      setWindError("Failed to fetch wind data");
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Enter Coordinates for Renewable Data</CardTitle>
          <CardDescription>Provide longitude and latitude for data calculations</CardDescription>
        </CardHeader>
        
        <CardContent>
          <Input
            type="text"
            placeholder="Enter longitude"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Enter latitude"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
          />
        </CardContent>
        
        <CardFooter>
          <Button onClick={handleSolarSubmit}>Submit Solar Data</Button>
          <Button onClick={handleWindSubmit} className="ml-4">Submit Wind Data</Button>
        </CardFooter>

        {solarError && <p className="text-red-500">{solarError}</p>}
        {windError && <p className="text-red-500">{windError}</p>}

        {solarResult && (
          <div className="p-4 mt-4 bg-gray-100 rounded-md">
            <h3>Solar Data Results</h3>
            <p>Annual AC Output (kWh): {solarResult.ac_annual}</p>
            <p>Solar Radiation (kWh/m²/day): {solarResult.solrad_annual}</p>
            <p>Capacity Factor (%): {solarResult.capacity_factor}</p>
            <p>Panel Area (m²): {solarResult.panel_area}</p>
            <p>Annual Cost Savings (USD): {solarResult.annual_cost_savings}</p>
            <p>ROI (years): {solarResult.roi_years}</p>
            <p>CO2 Reduction (kg): {solarResult.co2_reduction}</p>
          </div>
        )}

        {windResult && (
          <div className="p-4 mt-4 bg-gray-100 rounded-md">
            <h3>Wind Data Results</h3>
            <p>Total Energy Generated (kWh): {windResult.total_energy_kwh}</p>
            <p>Capacity Factor (%): {windResult.capacity_factor_percentage}</p>
            <p>Message: {windResult.message}</p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default HomePage;
