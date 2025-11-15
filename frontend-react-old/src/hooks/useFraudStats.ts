import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useFraudStats() {
  return useQuery({
    queryKey: ['fraudStats'],
    queryFn: () => api.getStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useTrends(days: number = 30) {
  return useQuery({
    queryKey: ['trends', days],
    queryFn: () => api.getTrends(days),
    refetchInterval: 60000, // Refetch every 60 seconds
  });
}

export function useTopOffenders(limit: number = 10) {
  return useQuery({
    queryKey: ['topOffenders', limit],
    queryFn: () => api.getTopOffenders(limit),
    refetchInterval: 60000,
  });
}

export function useRecentFlags(type: 'review' | 'transaction', limit: number = 20) {
  return useQuery({
    queryKey: ['recentFlags', type, limit],
    queryFn: () => api.getRecentFlags(type, limit),
    refetchInterval: 10000, // Refetch every 10 seconds for recent data
  });
}
