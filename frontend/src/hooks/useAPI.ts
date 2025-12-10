import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { api, DashboardStats, TrendData, TopOffender, RecentFlag } from '../services/api';

export function useDashboardStats(): UseQueryResult<DashboardStats> {
  return useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => api.getStats(),
    refetchInterval: 60000, // Refetch every 60 seconds
    staleTime: 30000,
    retry: 1,
  });
}

export function useTrends(days: number = 30): UseQueryResult<{ reviews: TrendData[]; transactions: TrendData[] }> {
  return useQuery({
    queryKey: ['trends', days],
    queryFn: () => api.getTrends(days),
    refetchInterval: 120000, // Refetch every 2 minutes
    staleTime: 60000,
    retry: 1,
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
    refetchInterval: 120000, // Refetch every 2 minutes
    staleTime: 60000,
    retry: 1,
  });
}

export function useRecentFlags(type: 'review' | 'transaction', limit: number = 20): UseQueryResult<{ items: RecentFlag[] }> {
  return useQuery({
    queryKey: ['recentFlags', type, limit],
    queryFn: () => api.getRecentFlags(type, limit),
    refetchInterval: 60000, // Refetch every 60 seconds
    staleTime: 30000,
    retry: 1,
  });
}

export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.healthCheck(),
    refetchInterval: 60000,
    staleTime: 30000,
    retry: 1,
  });
}

// New hooks for dynamic data
export function useAllReviews(page: number = 1, perPage: number = 50, filter: string = 'all') {
  return useQuery({
    queryKey: ['allReviews', page, perPage, filter],
    queryFn: () => api.getAllReviews(page, perPage, filter),
    refetchInterval: 60000, // Refetch every 60 seconds
    staleTime: 30000,
    retry: 1,
  });
}

export function useAllTransactions(page: number = 1, perPage: number = 50, filter: string = 'all') {
  return useQuery({
    queryKey: ['allTransactions', page, perPage, filter],
    queryFn: () => api.getAllTransactions(page, perPage, filter),
    refetchInterval: 60000, // Refetch every 60 seconds
    staleTime: 30000,
    retry: 1,
  });
}

export function useModelMetrics() {
  return useQuery({
    queryKey: ['modelMetrics'],
    queryFn: () => api.getModelMetrics(),
    refetchInterval: 120000, // Refetch every 2 minutes
    staleTime: 60000,
    retry: 1,
  });
}
