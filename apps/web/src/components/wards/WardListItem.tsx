'use client';

import RiskBadge from '@/components/common/RiskBadge';
import HSRIIndicator from '@/components/risk/HSRIIndicator';

interface WardListItemProps {
  id: string;
  name: string;
  city: string;
  population: number | null;
  riskCategory: string | null;
  hsri: number | null;
}

export default function WardListItem({
  id,
  name,
  city,
  population,
  riskCategory,
  hsri,
}: WardListItemProps) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold">{name}</h3>
          <p className="text-sm text-gray-500">{city}</p>
          {population && (
            <p className="text-sm text-gray-500">
              Population: {population.toLocaleString()}
            </p>
          )}
        </div>
        <div className="text-right">
          {riskCategory && <RiskBadge category={riskCategory as 'low' | 'medium' | 'high'} />}
          {hsri !== null && (
            <div className="mt-2 w-32">
              <HSRIIndicator value={hsri} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
