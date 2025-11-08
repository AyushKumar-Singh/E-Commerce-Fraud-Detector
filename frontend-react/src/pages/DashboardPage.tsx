import React from 'react';
import { useFraudStats, useTrends, useTopOffenders, useRecentFlags } from '@/hooks/useFraudStats';
import { StatsCard } from '@/components/Dashboard/StatsCard';
import { TrendChart } from '@/components/Dashboard/TrendChart';
import { Card } from '@/components/common/Card';
import { Loader2, AlertTriangle } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading: statsLoading } = useFraudStats();
  const { data: trends, isLoading: trendsLoading } = useTrends(30);
  const { data: offenders, isLoading: offendersLoading } = useTopOffenders();
  const { data: recentReviews } = useRecentFlags('review');

  if (statsLoading || trendsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Fraud Detection Dashboard</h1>
        <p className="mt-2 text-gray-600">Real-time monitoring and analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Reviews Today"
          value={stats?.reviews.today.total || 0}
          subtitle={`${stats?.reviews.today.flagged || 0} flagged`}
          icon="activity"
          color="blue"
        />
        <StatsCard
          title="Fraud Rate (Today)"
          value={`${((stats?.reviews.today.flagged || 0) / (stats?.reviews.today.total || 1) * 100).toFixed(1)}%`}
          subtitle="Review fraud rate"
          icon="down"
          color="red"
        />
        <StatsCard
          title="Transactions Today"
          value={stats?.transactions.today.total || 0}
          subtitle={`₹${(stats?.transactions.today.total_amount || 0).toLocaleString()}`}
          icon="up"
          color="green"
        />
        <StatsCard
          title="Flagged Amount"
          value={`₹${(stats?.transactions.today.flagged_amount || 0).toLocaleString()}`}
          subtitle={`${stats?.transactions.today.flagged || 0} transactions`}
          icon="activity"
          color="yellow"
        />
      </div>

      {/* Trend Chart */}
      {trends && (
        <Card title="Fraud Trends (Last 30 Days)" subtitle="Daily fraud detection rates">
          <TrendChart reviewData={trends.reviews} transactionData={trends.transactions} />
        </Card>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Offending IPs */}
        <Card title="Top Flagged IPs" subtitle="Last 7 days">
          {offendersLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-600 border-b">
                    <th className="pb-3 font-medium">IP Address</th>
                    <th className="pb-3 font-medium">Total</th>
                    <th className="pb-3 font-medium">Flagged</th>
                    <th className="pb-3 font-medium">Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {offenders?.ips.slice(0, 5).map((ip, idx) => (
                    <tr key={idx} className="text-sm">
                      <td className="py-3 font-mono text-gray-900">{ip.ip}</td>
                      <td className="py-3 text-gray-600">{ip.total}</td>
                      <td className="py-3">
                        <span className="px-2 py-1 bg-danger-50 text-danger-700 rounded-full text-xs font-semibold">
                          {ip.flagged}
                        </span>
                      </td>
                      <td className="py-3 font-semibold text-gray-900">{ip.flag_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Recent Flagged Reviews */}
        <Card title="Recent Flagged Reviews" subtitle="Latest suspicious activity">
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentReviews?.items.slice(0, 5).map((item) => (
              <div key={item.id} className="p-3 bg-red-50 rounded-lg border border-red-100">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span className="text-xs font-medium text-red-900">User {item.user_id}</span>
                  </div>
                  <span className="text-xs text-red-600 font-semibold">
                    {(item.score * 100).toFixed(0)}% fraud
                  </span>
                </div>
                <p className="text-sm text-gray-700 line-clamp-2">{item.text}</p>
                {item.reasons.length > 0 && (
                  <p className="mt-2 text-xs text-red-700">
                    {item.reasons[0]}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};