'use client';

interface MapContainerProps {
  center?: [number, number];
  zoom?: number;
}

export default function MapContainer({
  center = [78.9629, 22.5937], // India center
  zoom = 5,
}: MapContainerProps) {
  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="h-[500px] bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-2">MapLibre GL JS</p>
          <p className="text-sm text-gray-400">
            Center: [{center[0]}, {center[1]}] | Zoom: {zoom}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Interactive map will be initialized here
          </p>
        </div>
      </div>
    </div>
  );
}
