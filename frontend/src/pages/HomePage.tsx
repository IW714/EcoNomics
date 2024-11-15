import React, { useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable';
import { Button } from '@/components/ui/button';
import ChatWidget from './ChatWidget';
import { SolarAssessmentResponse, WindDataResponse } from '@/models/types';
import { getCoordinates, calculateSolarPotential, processWindData } from '@/services/apiService';
import { Input } from '@/components/ui/input';

const HomePage: React.FC = () => {
  const [cityName, setCityName] = useState('');
  const [latitude, setLatitude] = useState(0);
  const [longitude, setLongitude] = useState(0);
  const [solarResult, setSolarResult] = useState<SolarAssessmentResponse | null>(null);
  const [windResult, setWindResult] = useState<WindDataResponse | null>(null);
  const [solarError, setSolarError] = useState("");
  const [windError, setWindError] = useState("");
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleLatitudeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLatitude(parseFloat(e.target.value));
  };
  
  const handleLongitudeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLongitude(parseFloat(e.target.value));
  };

  // Updated handler to accept assessment data from the chat
  const handleCombinedAssessmentResult = useCallback(
    (solarAssessment: SolarAssessmentResponse, windAssessment: WindDataResponse) => {
      setSolarResult(solarAssessment);
      setWindResult(windAssessment);
    },
    []
  );
  
  const getCoords = async () => {
    if (cityName.trim()) {
      try {
        const coords = await getCoordinates({ city_name: cityName.trim() });
        setLatitude(coords.latitude);
        setLongitude(coords.longitude);
        return coords;
      } catch (err) {
        console.error("Failed to fetch coordinates:", err);
        throw new Error("Failed to get coordinates for the provided city name");
      }
    }
    return null;
  };

  const validateCoordinates = (lat: number, lon: number): boolean => {
    return !isNaN(lat) && !isNaN(lon) && 
           lat >= -90 && lat <= 90 && 
           lon >= -180 && lon <= 180;
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
    <div className="bg-background min-h-screen container mx-auto p-4">
      <ResizablePanelGroup
        direction="horizontal"
        className="min-h-[800px] rounded-lg"
      >
        {/* Chat Panel */}
        <ResizablePanel defaultSize={40} minSize={30}>
          <div className="h-full p-4">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Chat Assistance</CardTitle>
              </CardHeader>
              <CardContent className="h-[calc(100%-5rem)] overflow-y-auto">
                <ChatWidget 
                  onCombinedAssessmentResult={handleCombinedAssessmentResult}
                />
              </CardContent>
            </Card>
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Assessment Panel */}
        <ResizablePanel defaultSize={60} minSize={30}>
          <div className="h-full p-4">
            <Card className="h-full overflow-y-auto">
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

                  <div className="text-center text-muted-foreground">- OR -</div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Latitude</label>
                      <Input
                        type="number"
                        placeholder="Enter latitude"
                        value={latitude}
                        onChange={handleLatitudeChange}
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
                        onChange={handleLongitudeChange}
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
                  <div className="w-full p-4 bg-destructive/10 border border-destructive/20 rounded-md">
                    {solarError && <p className="text-destructive">{solarError}</p>}
                    {windError && <p className="text-destructive">{windError}</p>}
                  </div>
                )}
              </CardFooter>

              {/* Display Results */}
              {(solarResult || windResult) && (
                <div className="p-6 border-t border-border">
                  {/* Solar Results */}
                  {solarResult && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-4">Solar Assessment Results</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Annual AC Output</p>
                          <p className="text-lg text-foreground">{solarResult.ac_annual.toFixed(2)} kWh</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Solar Radiation</p>
                          <p className="text-lg text-foreground">{solarResult.solrad_annual.toFixed(2)} kWh/m²/day</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Capacity Factor</p>
                          <p className="text-lg text-foreground">{(solarResult.capacity_factor * 100).toFixed(1)}%</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Panel Area</p>
                          <p className="text-lg text-foreground">{solarResult.panel_area.toFixed(2)} m²</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Annual Savings</p>
                          <p className="text-lg text-foreground">${solarResult.annual_cost_savings.toFixed(2)}</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">ROI Period</p>
                          <p className="text-lg text-foreground">{solarResult.roi_years.toFixed(1)} years</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md col-span-2">
                          <p className="text-sm font-medium text-muted-foreground">CO₂ Reduction</p>
                          <p className="text-lg text-foreground">{solarResult.co2_reduction.toFixed(2)} kg/year</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Wind Results */}
                  {windResult && (
                    <div>
                      <h3 className="text-lg font-semibold mb-4">Wind Assessment Results</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Annual Energy Output</p>
                          <p className="text-lg text-foreground">{windResult.total_energy_kwh.toFixed(2)} kWh</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Capacity Factor</p>
                          <p className="text-lg text-foreground">{windResult.capacity_factor_percentage.toFixed(1)}%</p>
                        </div>
                        <div className="p-4 bg-muted rounded-md">
                          <p className="text-sm font-medium text-muted-foreground">Annual Savings</p>
                          <p className="text-lg text-foreground">${windResult.cost_savings.toFixed(2)}</p>
                        </div>
                        {windResult.message && (
                          <div className="p-4 bg-warning/10 border border-warning/20 rounded-md col-span-2">
                            <p className="text-warning-foreground">{windResult.message}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </Card>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default HomePage;
