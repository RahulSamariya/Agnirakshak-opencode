'use client';

import Link from 'next/link';

export default function DashboardPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Dashboard</h1>
      <p className="text-lg text-gray-600 mb-8">
        Overview of current heatwave conditions across India
      </p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="p-6 border rounded-lg shadow-sm bg-green-50">
          <h3 className="text-sm font-medium text-green-800">Low Risk Areas</h3>
          <p className="text-3xl font-bold text-green-600">--</p>
        </div>
        <div className="p-6 border rounded-lg shadow-sm bg-yellow-50">
          <h3 className="text-sm font-medium text-yellow-800">Medium Risk Areas</h3>
          <p className="text-3xl font-bold text-yellow-600">--</p>
        </div>
        <div className="p-6 border rounded-lg shadow-sm bg-red-50">
          <h3 className="text-sm font-medium text-red-800">High Risk Areas</h3>
          <p className="text-3xl font-bold text-red-600">--</p>
        </div>
        <div className="p-6 border rounded-lg shadow-sm bg-blue-50">
          <h3 className="text-sm font-medium text-blue-800">Active Alerts</h3>
          <p className="text-3xl font-bold text-blue-600">--</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/risk-map" className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold mb-2">Risk Map</h2>
          <p className="text-gray-500">View spatial risk visualization</p>
        </Link>
        <Link href="/wards" className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold mb-2">Ward Explorer</h2>
          <p className="text-gray-500">Explore ward-level risk data</p>
        </Link>
        <Link href="/forecasts" className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold mb-2">Forecasts</h2>
          <p className="text-gray-500">View weather forecast data</p>
        </Link>
        <Link href="/alerts" className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold mb-2">Alert Center</h2>
          <p className="text-gray-500">Manage active warnings</p>
        </Link>
      </div>
    </main>
  );
}
