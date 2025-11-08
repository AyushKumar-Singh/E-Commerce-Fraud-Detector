import axios, { AxiosInstance } from 'axios';
import { 
  ReviewPayload, 
  TransactionPayload, 
  ReviewPrediction, 
  TransactionPrediction,
  FraudStats,
  TrendData,
  TopOffender,
  RecentFlag
} from '@/types';

class FraudDetectorAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('api_token');
        if (token) {
          config.headers['X-API-Key'] = token;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('api_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck() {
    const { data } = await this.client.get('/health');
    return data;
  }

  // Predictions
  async predictReview(payload: ReviewPayload): Promise<ReviewPrediction> {
    const { data } = await this.client.post('/predict/review', payload);
    return data;
  }

  async predictTransaction(payload: TransactionPayload): Promise<TransactionPrediction> {
    const { data } = await this.client.post('/predict/transaction', payload);
    return data;
  }

  // Dashboard data
  async getStats(): Promise<FraudStats> {
    const { data } = await this.client.get('/dashboard/api/stats');
    return data;
  }

  async getTrends(days: number = 30): Promise<{ reviews: TrendData[]; transactions: TrendData[] }> {
    const { data } = await this.client.get(`/dashboard/api/trends?days=${days}`);
    return data;
  }

  async getTopOffenders(limit: number = 10): Promise<{
    ips: TopOffender[];
    devices: TopOffender[];
    users: TopOffender[];
  }> {
    const { data } = await this.client.get(`/dashboard/api/top-offenders?limit=${limit}`);
    return data;
  }

  async getRecentFlags(type: 'review' | 'transaction', limit: number = 20): Promise<{ items: RecentFlag[] }> {
    const { data } = await this.client.get(`/dashboard/api/recent-flags?type=${type}&limit=${limit}`);
    return data;
  }

  // Authentication
  async login(secret: string): Promise<{ token: string }> {
    const { data } = await this.client.post('/auth/token', { secret });
    return data;
  }
}

export const api = new FraudDetectorAPI();