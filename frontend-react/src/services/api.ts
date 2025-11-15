import axios, { AxiosInstance } from 'axios';

export interface Transaction {
  id: string | number;
  user_id: number;
  amount: number;
  timestamp?: string;
  created_at: string;
  status: 'flagged' | 'safe' | 'pending';
  fraud_score: number;
  confidence_score?: number;
  location?: string;
  ip_address?: string;
  device_fingerprint?: string;
  channel?: string;
  currency?: string;
  is_fraud_pred: boolean;
  decision_json?: {
    decision: boolean;
    score_final: number;
    score_model: number;
    score_rules: number;
    confidence: string;
    reasons: string[];
  };
}

export interface Review {
  id: string | number;
  product_id?: string;
  user_id: number;
  review_text: string;
  rating: number;
  sentiment?: 'Positive' | 'Neutral' | 'Fake';
  sentiment_score?: number;
  confidence_score?: number;
  created_at: string;
  timestamp?: string;
  ip_address?: string;
  device_fingerprint?: string;
  is_fake_pred: boolean;
  fake_score: number;
  decision_json?: {
    decision: boolean;
    score_final: number;
    score_model: number;
    score_rules: number;
    confidence: string;
    reasons: string[];
  };
}

export interface DashboardStats {
  reviews: {
    today: { total: number; flagged: number };
    week: { total: number; flagged: number };
    month: { total: number; flagged: number };
  };
  transactions: {
    today: { total: number; flagged: number; total_amount: number; flagged_amount: number };
    week: { total: number; flagged: number };
    month: { total: number; flagged: number };
  };
  timestamp: string;
}

export interface TrendData {
  date: string;
  total: number;
  flagged: number;
  avg_score: number;
  flag_rate: number;
  total_amount?: number;
}

export interface TopOffender {
  ip?: string;
  device?: string;
  user_id?: number;
  email?: string;
  total: number;
  flagged: number;
  flag_rate: number;
  total_amount?: number;
}

export interface RecentFlag {
  id: number;
  user_id: number;
  product_id?: string;
  text?: string;
  rating?: number;
  amount?: number;
  currency?: string;
  score: number;
  reasons: string[];
  created_at: string;
  ip?: string;
  channel?: string;
}

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
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
        // Don't redirect on login endpoint failures
        if (error.response?.status === 401 && !error.config?.url?.includes('/auth/token')) {
          localStorage.removeItem('api_token');
          // Force app re-render by dispatching storage event
          window.dispatchEvent(new Event('storage'));
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

  // Authentication
  async login(secret: string): Promise<{ token: string }> {
    const { data } = await this.client.post('/auth/token', { secret });
    return data;
  }

  // Dashboard data
  async getStats(): Promise<DashboardStats> {
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

  // Predictions
  async predictReview(payload: {
    user_id: number;
    product_id?: string;
    review_text: string;
    rating: number;
    ip_address?: string;
    device_fingerprint?: string;
  }) {
    const { data } = await this.client.post('/predict/review', payload);
    return data;
  }

  async predictTransaction(payload: {
    user_id: number;
    amount: number;
    currency?: string;
    channel?: string;
    ip_address?: string;
    device_fingerprint?: string;
  }) {
    const { data } = await this.client.post('/predict/transaction', payload);
    return data;
  }
}

export const api = new APIService();
