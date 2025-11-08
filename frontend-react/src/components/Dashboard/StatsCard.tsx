import React from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import clsx from 'clsx';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: number;
  subtitle?: string;
  icon?: 'up' | 'down' | 'activity';
  color?: 'blue' | 'red' | 'green' | 'yellow';
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  subtitle,
  icon = 'activity',
  color = 'blue',
}) => {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
  };

  const Icon = icon === 'up' ? TrendingUp : icon === 'down' ? TrendingDown : Activity;

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 uppercase tracking-wider">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-2 text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
        <div className={clsx('p-3 rounded-full', colors[color])}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      {change !== undefined && (
        <div className="mt-4 flex items-center">
          <span className={clsx('text-sm font-semibold', change >= 0 ? 'text-green-600' : 'text-red-600')}>
            {change >= 0 ? '+' : ''}{change}%
          </span>
          <span className="ml-2 text-sm text-gray-500">vs last period</span>
        </div>
      )}
    </div>
  );
};