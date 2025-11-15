export interface Transaction {
  id: string;
  userId: string;
  amount: number;
  timestamp: string;
  status: 'flagged' | 'safe' | 'pending';
  fraudScore: number;
  confidenceScore: number;
  location: string;
  paymentMethod: string;
  deviceId: string;
  ipAddress: string;
  transactionVelocity: number;
  detectionMethod: 'isolation-forest' | 'rule-based' | 'hybrid';
  riskFactors: string[];
}

export interface Review {
  id: string;
  productId: string;
  userId: string;
  text: string;
  rating: number;
  sentiment: 'Positive' | 'Neutral' | 'Fake';
  sentimentScore: number;
  confidenceScore: number;
  timestamp: string;
  accountAge: number;
  reviewFrequency: number;
  detectionMethod: 'nlp-sentiment' | 'rule-based' | 'hybrid';
  suspiciousPatterns: string[];
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'analyst' | 'viewer';
  status: 'active' | 'inactive';
  lastLogin: string;
}

export const mockTransactions: Transaction[] = [
  {
    id: 'TXN-001',
    userId: 'USR-1234',
    amount: 2499.99,
    timestamp: '2025-11-09T10:30:00',
    status: 'flagged',
    fraudScore: 87,
    confidenceScore: 92,
    location: 'New York, USA',
    paymentMethod: 'Credit Card',
    deviceId: 'DEV-9876',
    ipAddress: '192.168.1.45',
    transactionVelocity: 5,
    detectionMethod: 'isolation-forest',
    riskFactors: ['High velocity', 'New device', 'Unusual amount'],
  },
  {
    id: 'TXN-002',
    userId: 'USR-5678',
    amount: 149.99,
    timestamp: '2025-11-09T09:15:00',
    status: 'safe',
    fraudScore: 12,
    confidenceScore: 95,
    location: 'Los Angeles, USA',
    paymentMethod: 'PayPal',
    deviceId: 'DEV-1234',
    ipAddress: '192.168.1.23',
    transactionVelocity: 1,
    detectionMethod: 'hybrid',
    riskFactors: [],
  },
  {
    id: 'TXN-003',
    userId: 'USR-9012',
    amount: 5799.50,
    timestamp: '2025-11-09T08:45:00',
    status: 'flagged',
    fraudScore: 92,
    confidenceScore: 88,
    location: 'London, UK',
    paymentMethod: 'Debit Card',
    deviceId: 'DEV-5555',
    ipAddress: '10.0.0.89',
    transactionVelocity: 8,
    detectionMethod: 'isolation-forest',
    riskFactors: ['Spending spike', 'Geo-anomaly', 'High velocity'],
  },
  {
    id: 'TXN-004',
    userId: 'USR-3456',
    amount: 89.99,
    timestamp: '2025-11-09T11:20:00',
    status: 'safe',
    fraudScore: 8,
    confidenceScore: 97,
    location: 'Chicago, USA',
    paymentMethod: 'Credit Card',
    deviceId: 'DEV-2341',
    ipAddress: '192.168.2.10',
    transactionVelocity: 1,
    detectionMethod: 'hybrid',
    riskFactors: [],
  },
  {
    id: 'TXN-005',
    userId: 'USR-7890',
    amount: 3299.00,
    timestamp: '2025-11-09T07:50:00',
    status: 'pending',
    fraudScore: 54,
    confidenceScore: 76,
    location: 'Tokyo, Japan',
    paymentMethod: 'Apple Pay',
    deviceId: 'DEV-7788',
    ipAddress: '172.16.0.45',
    transactionVelocity: 3,
    detectionMethod: 'rule-based',
    riskFactors: ['Medium velocity', 'Large amount'],
  },
];

export const mockReviews: Review[] = [
  {
    id: 'REV-001',
    productId: 'PRD-123',
    userId: 'USR-1111',
    text: 'Great product! Exceeded my expectations. Fast shipping and excellent quality.',
    rating: 5,
    sentiment: 'Positive',
    sentimentScore: 0.92,
    confidenceScore: 94,
    timestamp: '2025-11-08T14:30:00',
    accountAge: 245,
    reviewFrequency: 2,
    detectionMethod: 'nlp-sentiment',
    suspiciousPatterns: [],
  },
  {
    id: 'REV-002',
    productId: 'PRD-456',
    userId: 'USR-2222',
    text: 'Best product ever!!! Amazing!!! Buy now!!!',
    rating: 5,
    sentiment: 'Fake',
    sentimentScore: 0.15,
    confidenceScore: 89,
    timestamp: '2025-11-08T15:45:00',
    accountAge: 3,
    reviewFrequency: 15,
    detectionMethod: 'hybrid',
    suspiciousPatterns: ['Excessive punctuation', 'Generic praise', 'New account'],
  },
  {
    id: 'REV-003',
    productId: 'PRD-789',
    userId: 'USR-3333',
    text: 'Product is okay. Nothing special, but it works as described.',
    rating: 3,
    sentiment: 'Neutral',
    sentimentScore: 0.48,
    confidenceScore: 91,
    timestamp: '2025-11-09T09:00:00',
    accountAge: 120,
    reviewFrequency: 5,
    detectionMethod: 'nlp-sentiment',
    suspiciousPatterns: [],
  },
  {
    id: 'REV-004',
    productId: 'PRD-101',
    userId: 'USR-4444',
    text: 'Absolutely love it! The quality is outstanding and delivery was quick.',
    rating: 5,
    sentiment: 'Positive',
    sentimentScore: 0.88,
    confidenceScore: 93,
    timestamp: '2025-11-09T10:15:00',
    accountAge: 380,
    reviewFrequency: 3,
    detectionMethod: 'nlp-sentiment',
    suspiciousPatterns: [],
  },
  {
    id: 'REV-005',
    productId: 'PRD-202',
    userId: 'USR-5555',
    text: 'PERFECT!!! BEST DEAL!!! DONT MISS!!!',
    rating: 5,
    sentiment: 'Fake',
    sentimentScore: 0.22,
    confidenceScore: 87,
    timestamp: '2025-11-09T11:30:00',
    accountAge: 1,
    reviewFrequency: 22,
    detectionMethod: 'hybrid',
    suspiciousPatterns: ['All caps text', 'Bot-like pattern', 'High frequency'],
  },
];

export const mockUsers: User[] = [
  {
    id: 'USR-001',
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2025-11-09T12:00:00',
  },
  {
    id: 'USR-002',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    role: 'analyst',
    status: 'active',
    lastLogin: '2025-11-09T10:30:00',
  },
  {
    id: 'USR-003',
    name: 'Bob Johnson',
    email: 'bob.johnson@example.com',
    role: 'viewer',
    status: 'active',
    lastLogin: '2025-11-08T16:45:00',
  },
  {
    id: 'USR-004',
    name: 'Alice Williams',
    email: 'alice.williams@example.com',
    role: 'analyst',
    status: 'inactive',
    lastLogin: '2025-11-05T09:20:00',
  },
];

export const dashboardStats = {
  fraudDetectionRate: 94.5,
  totalTransactions: 12847,
  flaggedTransactions: 342,
  totalReviews: 8563,
  fakeReviews: 287,
  falsePositiveRate: 2.3,
  modelAccuracy: 96.2,
  averageConfidence: 91.5,
};

export const fraudTrendData = [
  { month: 'Jun', fraudScore: 12, transactions: 980 },
  { month: 'Jul', fraudScore: 18, transactions: 1250 },
  { month: 'Aug', fraudScore: 15, transactions: 1180 },
  { month: 'Sep', fraudScore: 22, transactions: 1420 },
  { month: 'Oct', fraudScore: 28, transactions: 1680 },
  { month: 'Nov', fraudScore: 24, transactions: 1550 },
];

export const sentimentDistribution = [
  { name: 'Positive', value: 6890, percentage: 80.5 },
  { name: 'Neutral', value: 1386, percentage: 16.2 },
  { name: 'Fake', value: 287, percentage: 3.3 },
];

export const modelPerformanceData = {
  isolationForest: {
    accuracy: 94.5,
    precision: 92.3,
    recall: 96.1,
    f1Score: 94.2,
  },
  nlpSentiment: {
    accuracy: 91.8,
    precision: 89.5,
    recall: 93.4,
    f1Score: 91.4,
  },
};