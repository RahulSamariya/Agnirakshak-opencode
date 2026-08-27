'use client';

export default function AlertsPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Alert Center</h1>
      <p className="text-lg text-gray-600 mb-8">
        Active warnings and operational recommendations
      </p>

      <div className="border rounded-lg shadow-sm p-6">
        <div className="mb-4 flex gap-4">
          <button className="px-4 py-2 bg-blue-500 text-white rounded" disabled>
            All
          </button>
          <button className="px-4 py-2 border rounded" disabled>
            Critical
          </button>
          <button className="px-4 py-2 border rounded" disabled>
            Warning
          </button>
          <button className="px-4 py-2 border rounded" disabled>
            Info
          </button>
        </div>
        <div className="text-center py-12 text-gray-500">
          <p>Active alerts will be displayed here</p>
          <p className="text-sm mt-2">Each alert includes action recommendations</p>
        </div>
      </div>
    </main>
  );
}
