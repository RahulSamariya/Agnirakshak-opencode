'use client';

interface RiskCardProps {
  title: string;
  hazard: number;
  vulnerability: number;
  exposure: number;
  hsri: number;
  riskCategory: string;
}

export default function RiskCard({
  title,
  hazard,
  vulnerability,
  exposure,
  hsri,
  riskCategory,
}: RiskCardProps) {
  return (
    <div className="border rounded-lg shadow-sm p-4">
      <h3 className="font-semibold mb-2">{title}</h3>
      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Hazard:</span>
          <span>{(hazard * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Vulnerability:</span>
          <span>{(vulnerability * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Exposure:</span>
          <span>{(exposure * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between font-medium">
          <span className="text-gray-500">HSRI:</span>
          <span>{(hsri * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Category:</span>
          <span className="uppercase">{riskCategory}</span>
        </div>
      </div>
    </div>
  );
}
