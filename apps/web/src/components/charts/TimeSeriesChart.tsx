'use client';

interface TimeSeriesChartProps {
  data: Array<{ time: string; value: number }>;
  title: string;
  yLabel?: string;
}

export default function TimeSeriesChart({
  data,
  title,
  yLabel,
}: TimeSeriesChartProps) {
  return (
    <div className="border rounded-lg shadow-sm p-4">
      <h3 className="font-semibold mb-2">{title}</h3>
      <div className="h-[200px] bg-gray-50 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p>Recharts/ECharts will render here</p>
          <p className="text-sm mt-1">
            {data.length} data points | Y-axis: {yLabel || 'value'}
          </p>
        </div>
      </div>
    </div>
  );
}
