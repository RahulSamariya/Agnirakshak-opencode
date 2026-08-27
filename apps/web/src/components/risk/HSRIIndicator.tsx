'use client';

interface HSRIIndicatorProps {
  value: number;
  showLabel?: boolean;
}

export default function HSRIIndicator({ value, showLabel = true }: HSRIIndicatorProps) {
  const percentage = value * 100;

  const getColor = (v: number) => {
    if (v <= 0.33) return 'bg-green-500';
    if (v <= 0.66) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor(value)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
      )}
    </div>
  );
}
