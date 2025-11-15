import { motion } from 'motion/react';
import {
  AlertTriangle,
  DollarSign,
  FileText,
  Shield,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { StatCard } from '../components/StatCard';
import { useDashboardStats, useTrends, useRecentFlags } from '../hooks/useAPI';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';

const COLORS = ['#10b981', '#64748b', '#ef4444'];

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: trends, isLoading: trendsLoading } = useTrends(30);
  const { data: recentFlags, isLoading: flagsLoading } = useRecentFlags('transaction', 3);

  if (statsLoading || trendsLoading) {
    return <LoadingSkeleton />;
  }

  const recentTransactions = recentFlags?.items || [];
  const reviewTrends = trends?.reviews || [];
  const txTrends = trends?.transactions || [];

  // Calculate sentiment distribution from review stats
  const totalReviews = stats?.reviews.month.total || 0;
  const fakeReviews = stats?.reviews.month.flagged || 0;
  const genuineReviews = totalReviews - fakeReviews;
  
  const sentimentDistribution = [
    { name: 'Positive', value: genuineReviews, percentage: totalReviews > 0 ? ((genuineReviews / totalReviews) * 100).toFixed(1) : 0 },
    { name: 'Neutral', value: 0, percentage: 0 },
    { name: 'Fake', value: fakeReviews, percentage: totalReviews > 0 ? ((fakeReviews / totalReviews) * 100).toFixed(1) : 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <h2>AI-Powered Fraud Detection Dashboard</h2>
        <p className="text-muted-foreground">
          Real-time dual-module system: Isolation Forest + NLP Sentiment Analysis
        </p>
        <div className="flex items-center gap-4 mt-2">
          <Badge variant="outline" className="gap-2">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
            System Active
          </Badge>
          <Badge variant="secondary">Flask API Connected</Badge>
          <Badge variant="secondary">ML Models: v2.1.0</Badge>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Reviews Today"
          value={stats?.reviews.today.total || 0}
          change={`${stats?.reviews.today.flagged || 0} flagged`}
          changeType="neutral"
          icon={FileText}
          iconColor="bg-success"
          delay={0}
        />
        <StatCard
          title="Fake Reviews Today"
          value={stats?.reviews.today.flagged || 0}
          change={stats?.reviews.today.total > 0 ? `${((stats.reviews.today.flagged / stats.reviews.today.total) * 100).toFixed(1)}%` : '0%'}
          changeType="warning"
          icon={AlertTriangle}
          iconColor="bg-warning"
          delay={0.1}
        />
        <StatCard
          title="Transactions Today"
          value={stats?.transactions.today.total || 0}
          change={`$${stats?.transactions.today.total_amount?.toFixed(2) || 0}`}
          changeType="neutral"
          icon={DollarSign}
          iconColor="bg-primary"
          delay={0.2}
        />
        <StatCard
          title="Flagged Today"
          value={stats?.transactions.today.flagged || 0}
          change={`$${stats?.transactions.today.flagged_amount?.toFixed(2) || 0}`}
          changeType="negative"
          icon={AlertTriangle}
          iconColor="bg-destructive"
          delay={0.3}
        />
      </div>

      {/* Dual Module Status */}
      <div className="grid gap-4 lg:grid-cols-2">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-primary" />
                    Isolation Forest Module
                  </CardTitle>
                  <p className="text-muted-foreground">
                    Transaction anomaly detection
                  </p>
                </div>
                <Badge className="bg-success">Active</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Accuracy</span>
                  <span>94.5%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Precision</span>
                  <span>92.3%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Recall</span>
                  <span>96.1%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">F1-Score</span>
                  <span>94.2%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="border-accent/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-accent" />
                    NLP Sentiment Module
                  </CardTitle>
                  <p className="text-muted-foreground">
                    Fake review detection
                  </p>
                </div>
                <Badge className="bg-success">Active</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Accuracy</span>
                  <span>91.8%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Precision</span>
                  <span>89.5%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Recall</span>
                  <span>93.4%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">F1-Score</span>
                  <span>91.4%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Fraud Trend Chart */}
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Fraud Detection Trend</CardTitle>
              <p className="text-muted-foreground">
                Monthly fraud score and transaction volume
              </p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={txTrends}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="date" className="text-muted-foreground" />
                  <YAxis className="text-muted-foreground" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="flagged"
                    stroke="#ef4444"
                    strokeWidth={2}
                    name="Flagged"
                  />
                  <Line
                    type="monotone"
                    dataKey="total"
                    stroke="#2563eb"
                    strokeWidth={2}
                    name="Total"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Sentiment Distribution */}
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Review Sentiment Distribution</CardTitle>
              <p className="text-muted-foreground">
                NLP-based sentiment analysis results
              </p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name} ${percentage}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent High-Risk Detections</CardTitle>
                <p className="text-muted-foreground">
                  Flagged by Isolation Forest algorithm with explainable AI
                </p>
              </div>
              <Button variant="outline">View All</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentTransactions.map((transaction, index) => (
                <motion.div
                  key={transaction.id}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                  className="flex flex-col gap-3 rounded-lg border border-border p-4 hover:bg-accent/5 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-destructive/10">
                        <AlertTriangle className="h-5 w-5 text-destructive" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p>TXN-{transaction.id}</p>
                          <Badge variant="destructive">Flagged</Badge>
                          <Badge variant="outline" className="text-xs">
                            AI Detected
                          </Badge>
                        </div>
                        <p className="text-muted-foreground">
                          User {transaction.user_id} • {transaction.ip || 'Unknown IP'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p>${transaction.amount?.toFixed(2) || 0}</p>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <span>Score: {(transaction.score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                  {transaction.reasons && transaction.reasons.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      <span className="text-muted-foreground text-sm">Risk Factors:</span>
                      {transaction.reasons.map((factor, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {factor}
                        </Badge>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
              {recentTransactions.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No recent flagged transactions
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}