'use client';

import { RiskCategory } from '@/types';

interface RiskBadgeProps {
  category: RiskCategory;
  size?: 'sm' | 'md' | 'lg';
}

const categoryStyles: Record<RiskCategory, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
};

export default function RiskBadge({ category, size = 'md' }: RiskBadgeProps) {
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={`inline-block rounded-full font-medium ${categoryStyles[category]} ${sizeClasses[size]}`}
    >
      {category.toUpperCase()}
    </span>
  );
}
