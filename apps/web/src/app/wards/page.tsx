'use client';

export default function WardsPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Ward Explorer</h1>
      <p className="text-lg text-gray-600 mb-8">
        Explore ward-level risk and vulnerability data
      </p>

      <div className="border rounded-lg shadow-sm p-6">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search wards..."
            className="w-full p-2 border rounded"
            disabled
          />
        </div>
        <div className="text-center py-12 text-gray-500">
          <p>Ward list will be populated from the API</p>
          <p className="text-sm mt-2">Select a ward to view detailed risk breakdown</p>
        </div>
      </div>
    </main>
  );
}
