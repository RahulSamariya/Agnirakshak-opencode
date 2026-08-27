'use client';

export default function WardDetailPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Ward Details</h1>
      <p className="text-lg text-gray-600 mb-8">
        Detailed risk breakdown for the selected ward
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Risk Summary</h2>
          <div className="space-y-2">
            <p className="text-gray-500">HSRI: --</p>
            <p className="text-gray-500">Risk Category: --</p>
            <p className="text-gray-500">Grid Cells: --</p>
          </div>
        </div>
        <div className="border rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Component Breakdown</h2>
          <div className="space-y-2">
            <p className="text-gray-500">Hazard: --</p>
            <p className="text-gray-500">Vulnerability: --</p>
            <p className="text-gray-500">Exposure: --</p>
          </div>
        </div>
      </div>
    </main>
  );
}
