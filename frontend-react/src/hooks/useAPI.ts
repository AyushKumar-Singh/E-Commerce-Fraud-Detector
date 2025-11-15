import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { api, DashboardStats, TrendData, TopOffender, RecentFlag } from '../services/api';

export function useDashboardStats(): UseQueryResult<DashboardStats> {
  return useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => api.getStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useTrends(days: number = 30): UseQueryResult<{ reviews: TrendData[]; transactions: TrendData[] }> {
  return useQuery({
    queryKey: ['trends', days],
    queryFn: () => api.getTrends(days),
    refetchInterval: 60000, // Refetch every 60 seconds
  });
}

export function useTopOffenders(limit: number = 10): UseQueryResult<{
  ips: TopOffender[];
  devices: TopOffender[];
  users: TopOffender[];
}> {
  return useQuery({
    queryKey: ['topOffenders', limit],
    queryFn: () => api.getTopOffenders(limit),
    refetchInterval: 60000,
  });
}

export function useRecentFlags(type: 'review' | 'transaction', limit: number = 20): UseQueryResult<{ items: RecentFlag[] }> {
  return useQuery({
    queryKey: ['recentFlags', type, limit],
    queryFn: () => api.getRecentFlags(type, limit),
    refetchInterval: 10000, // Refetch every 10 seconds for recent data
  });
}

export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.healthCheck(),
    refetchInterval: 30000,
  });
}
