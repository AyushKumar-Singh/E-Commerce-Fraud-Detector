export interface ReviewPrediction {
  review_id: number;
  decision: boolean;
  confidence: 'low' | 'medium' | 'high';
  score_model: number;
  score_rules: number;
  score_final: number;
  threshold: number;
  reasons: string[];
  model_contribution: number;
  rules_contribution: number;
}

export interface TransactionPrediction {
  transaction_id: number;
  decision: boolean;
  confidence: 'low' | 'medium' | 'high';
  score_final: number;
  reasons: string[];
}

export interface ReviewPayload {
  user_id: number;
  product_id: string;
  review_text: string;
  rating: number;
  ip_address?: string;
  device_fingerprint?: string;
}

export interface TransactionPayload {
  user_id: number;
  amount: number;
  currency: string;
  channel: string;
  ip_address?: string;
  device_fingerprint?: string;
}

export interface FraudStats {
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
}

export interface TopOffender {
  ip?: string;
  device?: string;
  user_id?: number;
  email?: string;
  total: number;
  flagged: number;
  flag_rate: number;
}

export interface RecentFlag {
  id: number;
  user_id: number;
  text?: string;
  amount?: number;
  rating?: number;
  score: number;
  reasons: string[];
  created_at: string;
  ip: string | null;
}