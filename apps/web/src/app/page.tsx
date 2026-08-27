export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">
        Heatwave Early Warning Platform
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Extreme Heatwave Early Warning and Human Thermal Stress Index
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-2">Dashboard</h2>
          <p className="text-gray-500">Overview of current conditions</p>
        </div>
        <div className="p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-2">Risk Map</h2>
          <p className="text-gray-500">Spatial risk visualization</p>
        </div>
        <div className="p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-2">Alerts</h2>
          <p className="text-gray-500">Active warnings and alerts</p>
        </div>
      </div>
    </main>
  );
}
