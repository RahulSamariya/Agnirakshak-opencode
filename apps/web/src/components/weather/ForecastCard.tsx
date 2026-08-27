'use client';

interface ForecastCardProps {
  model: string;
  validTime: string;
  leadTimeHours: number;
  temperature: number | null;
  humidity: number | null;
  windSpeed: number | null;
}

export default function ForecastCard({
  model,
  validTime,
  leadTimeHours,
  temperature,
  humidity,
  windSpeed,
}: ForecastCardProps) {
  return (
    <div className="border rounded-lg shadow-sm p-4">
      <h3 className="font-semibold mb-2">{model}</h3>
      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Valid Time:</span>
          <span>{new Date(validTime).toLocaleString()}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Lead Time:</span>
          <span>{leadTimeHours}h</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Temperature:</span>
          <span>{temperature !== null ? `${temperature.toFixed(1)}°C` : '--'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Humidity:</span>
          <span>{humidity !== null ? `${humidity.toFixed(1)}%` : '--'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Wind:</span>
          <span>{windSpeed !== null ? `${windSpeed.toFixed(1)} m/s` : '--'}</span>
        </div>
      </div>
    </div>
  );
}
