'use client';

import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">
            Heatwave Platform
          </Link>
          <nav className="flex gap-6">
            <Link href="/risk-map" className="text-gray-600 hover:text-gray-900">
              Risk Map
            </Link>
            <Link href="/wards" className="text-gray-600 hover:text-gray-900">
              Wards
            </Link>
            <Link href="/forecasts" className="text-gray-600 hover:text-gray-900">
              Forecasts
            </Link>
            <Link href="/alerts" className="text-gray-600 hover:text-gray-900">
              Alerts
            </Link>
            <Link href="/models" className="text-gray-600 hover:text-gray-900">
              Models
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
