'use client';

export default function ForecastsPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Forecast Explorer</h1>
      <p className="text-lg text-gray-600 mb-8">
        View weather forecast data and model runs
      </p>

      <div className="border rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Forecast Runs</h2>
        <div className="text-center py-12 text-gray-500">
          <p>Forecast data will be populated from the API</p>
          <p className="text-sm mt-2">Distinguishes forecast run time vs valid time</p>
        </div>
      </div>
    </main>
  );
}
