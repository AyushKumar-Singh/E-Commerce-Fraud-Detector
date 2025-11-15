import { motion } from 'motion/react';
import { BarChart3, TrendingDown, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const performanceData = [
  { date: '2025-11-03', accuracy: 92, precision: 89, recall: 94 },
  { date: '2025-11-04', accuracy: 93, precision: 91, recall: 93 },
  { date: '2025-11-05', accuracy: 94, precision: 92, recall: 95 },
  { date: '2025-11-06', accuracy: 93, precision: 90, recall: 94 },
  { date: '2025-11-07', accuracy: 95, precision: 93, recall: 96 },
  { date: '2025-11-08', accuracy: 94, precision: 92, recall: 95 },
  { date: '2025-11-09', accuracy: 96, precision: 94, recall: 97 },
];

const categoryData = [
  { category: 'Electronics', fraudRate: 12 },
  { category: 'Fashion', fraudRate: 8 },
  { category: 'Home & Garden', fraudRate: 5 },
  { category: 'Sports', fraudRate: 6 },
  { category: 'Books', fraudRate: 3 },
  { category: 'Beauty', fraudRate: 7 },
];

const hourlyData = [
  { hour: '00:00', transactions: 45, flagged: 3 },
  { hour: '04:00', transactions: 28, flagged: 1 },
  { hour: '08:00', transactions: 156, flagged: 12 },
  { hour: '12:00', transactions: 289, flagged: 18 },
  { hour: '16:00', transactions: 234, flagged: 15 },
  { hour: '20:00', transactions: 198, flagged: 11 },
];

export function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <h2>Advanced Analytics</h2>
        <p className="text-muted-foreground">
          Deep insights into fraud detection performance and trends
        </p>
      </motion.div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Model Performance Over Time</CardTitle>
            <p className="text-muted-foreground">
              Tracking accuracy, precision, and recall metrics
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  dataKey="date"
                  className="text-muted-foreground"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis className="text-muted-foreground" domain={[80, 100]} />
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
                  dataKey="accuracy"
                  stroke="#2563eb"
                  strokeWidth={2}
                  name="Accuracy %"
                />
                <Line
                  type="monotone"
                  dataKey="precision"
                  stroke="#14b8a6"
                  strokeWidth={2}
                  name="Precision %"
                />
                <Line
                  type="monotone"
                  dataKey="recall"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  name="Recall %"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </motion.div>

      {/* Two Column Layout */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Category Analysis */}
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Fraud Rate by Category</CardTitle>
              <p className="text-muted-foreground">
                Which product categories have the highest fraud rates
              </p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis type="number" className="text-muted-foreground" />
                  <YAxis
                    dataKey="category"
                    type="category"
                    className="text-muted-foreground"
                    width={120}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="fraudRate" fill="#ef4444" name="Fraud Rate %" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Hourly Activity */}
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Hourly Transaction Activity</CardTitle>
              <p className="text-muted-foreground">
                Transaction volume and fraud detection by time of day
              </p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="hour" className="text-muted-foreground" />
                  <YAxis className="text-muted-foreground" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="transactions"
                    stackId="1"
                    stroke="#2563eb"
                    fill="#2563eb"
                    fillOpacity={0.6}
                    name="Total Transactions"
                  />
                  <Area
                    type="monotone"
                    dataKey="flagged"
                    stackId="2"
                    stroke="#ef4444"
                    fill="#ef4444"
                    fillOpacity={0.6}
                    name="Flagged"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Key Insights */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Key Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-lg border border-border p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-5 w-5 text-success" />
                  <p>Model Accuracy</p>
                </div>
                <p className="text-success mb-1">↑ 2.1%</p>
                <p className="text-muted-foreground">
                  Accuracy improved from 93.8% to 96.0% this week
                </p>
              </div>

              <div className="rounded-lg border border-border p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="h-5 w-5 text-destructive" />
                  <p>False Positives</p>
                </div>
                <p className="text-success mb-1">↓ 18%</p>
                <p className="text-muted-foreground">
                  Reduced false positive rate through model tuning
                </p>
              </div>

              <div className="rounded-lg border border-border p-4">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="h-5 w-5 text-primary" />
                  <p>Peak Hours</p>
                </div>
                <p className="mb-1">12:00 - 16:00</p>
                <p className="text-muted-foreground">
                  Highest transaction volume during lunch hours
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
