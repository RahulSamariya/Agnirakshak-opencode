'use client';

export default function ModelsPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Scientific Models</h1>
      <p className="text-lg text-gray-600 mb-8">
        Model transparency and configuration details
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-2">UTCI Model</h2>
          <p className="text-sm text-gray-500 mb-4">Universal Thermal Climate Index</p>
          <p className="text-gray-500">Version: --</p>
          <p className="text-gray-500">Status: --</p>
        </div>
        <div className="border rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-2">Vulnerability Model</h2>
          <p className="text-sm text-gray-500 mb-4">BBWM-derived vulnerability scoring</p>
          <p className="text-gray-500">Version: --</p>
          <p className="text-gray-500">Status: --</p>
        </div>
        <div className="border rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-2">Exposure Model</h2>
          <p className="text-sm text-gray-500 mb-4">BBWM-derived exposure scoring</p>
          <p className="text-gray-500">Version: --</p>
          <p className="text-gray-500">Status: --</p>
        </div>
        <div className="border rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-2">Risk Model</h2>
          <p className="text-sm text-gray-500 mb-4">HSRI = H x V x E multiplicative model</p>
          <p className="text-gray-500">Version: --</p>
          <p className="text-gray-500">Status: --</p>
        </div>
      </div>
    </main>
  );
}
