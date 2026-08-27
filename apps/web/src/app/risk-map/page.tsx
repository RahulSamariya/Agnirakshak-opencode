'use client';

export default function RiskMapPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Risk Map</h1>
      <p className="text-lg text-gray-600 mb-8">
        Interactive spatial visualization of heatwave risk
      </p>

      <div className="border rounded-lg shadow-sm h-[600px] bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-4">MapLibre GL JS will be initialized here</p>
          <p className="text-sm text-gray-400">
            Supporting layers: Risk, Hazard, Vulnerability, Exposure
          </p>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 border rounded-lg">
          <h3 className="font-semibold mb-2">Risk Layer</h3>
          <p className="text-sm text-gray-500">HSRI composite visualization</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h3 className="font-semibold mb-2">Hazard Layer</h3>
          <p className="text-sm text-gray-500">UTCI-based hazard index</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h3 className="font-semibold mb-2">Vulnerability Layer</h3>
          <p className="text-sm text-gray-500">Population vulnerability</p>
        </div>
      </div>
    </main>
  );
}
