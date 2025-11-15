import { motion } from 'motion/react';
import { useState } from 'react';
import { ArrowUpDown, Filter, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { useRecentFlags } from '../hooks/useAPI';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { useDebounce } from '../hooks/useDebounce';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';

export function TransactionsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'amount' | 'fraudScore' | 'timestamp'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedTransaction, setSelectedTransaction] = useState<any | null>(null);

  const { data, isLoading } = useRecentFlags('transaction', 100);
  const debouncedSearch = useDebounce(searchQuery, 300);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const transactions = data?.items || [];

  // Filter and sort transactions
  const filteredTransactions = transactions
    .filter((txn) => {
      const matchesSearch =
        txn.id.toString().toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        txn.user_id.toString().toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        (txn.ip || '').toLowerCase().includes(debouncedSearch.toLowerCase());
      return matchesSearch;
    })
    .sort((a, b) => {
      const multiplier = sortOrder === 'asc' ? 1 : -1;
      if (sortBy === 'amount') return ((a.amount || 0) - (b.amount || 0)) * multiplier;
      if (sortBy === 'fraudScore') return (a.score - b.score) * multiplier;
      return (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) * multiplier;
    });

  const toggleSort = (field: 'amount' | 'fraudScore' | 'timestamp') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <h2>Transaction Monitoring</h2>
        <p className="text-muted-foreground">
          Isolation Forest anomaly detection with real-time behavioral analysis
        </p>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search by ID, user, location..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Status Filter */}
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="flagged">Flagged</SelectItem>
                    <SelectItem value="safe">Safe</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Transactions Table */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>
              Transactions ({filteredTransactions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-border overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>User ID</TableHead>
                    <TableHead>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleSort('amount')}
                        className="flex items-center gap-1 -ml-3"
                      >
                        Amount
                        <ArrowUpDown className="h-3 w-3" />
                      </Button>
                    </TableHead>
                    <TableHead>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleSort('fraudScore')}
                        className="flex items-center gap-1 -ml-3"
                      >
                        Fraud Score
                        <ArrowUpDown className="h-3 w-3" />
                      </Button>
                    </TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleSort('timestamp')}
                        className="flex items-center gap-1 -ml-3"
                      >
                        Time
                        <ArrowUpDown className="h-3 w-3" />
                      </Button>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTransactions.map((txn, index) => (
                    <motion.tr
                      key={txn.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="cursor-pointer hover:bg-accent/5"
                      onClick={() => setSelectedTransaction(txn)}
                    >
                      <TableCell>TXN-{txn.id}</TableCell>
                      <TableCell className="text-muted-foreground">USR-{txn.user_id}</TableCell>
                      <TableCell>${txn.amount?.toFixed(2) || 0}</TableCell>
                      <TableCell>
                        <span
                          className={
                            txn.score > 0.7
                              ? 'text-destructive'
                              : txn.score > 0.4
                              ? 'text-warning'
                              : 'text-success'
                          }
                        >
                          {(txn.score * 100).toFixed(0)}%
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="destructive">
                          flagged
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{txn.ip || 'N/A'}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(txn.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </TableCell>
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Transaction Detail Modal */}
      <Dialog open={!!selectedTransaction} onOpenChange={() => setSelectedTransaction(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Explainable AI - Transaction Analysis</DialogTitle>
            <DialogDescription>
              Detailed fraud analysis for transaction {selectedTransaction?.id}
            </DialogDescription>
          </DialogHeader>
          {selectedTransaction && (
            <div className="space-y-4">
              {/* Detection Method */}
              <div className="rounded-lg bg-muted/50 p-4">
                <div className="flex items-center justify-between mb-2">
                  <p>Detection Method</p>
                  <Badge variant="outline">{selectedTransaction.detectionMethod}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-muted-foreground">Confidence Score</p>
                  <p className="text-success">{selectedTransaction.confidenceScore}%</p>
                </div>
              </div>

              {/* Transaction Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-muted-foreground">User ID</p>
                  <p>{selectedTransaction.userId}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Amount</p>
                  <p>${selectedTransaction.amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Fraud Score</p>
                  <p
                    className={
                      selectedTransaction.fraudScore > 70
                        ? 'text-destructive'
                        : selectedTransaction.fraudScore > 40
                        ? 'text-warning'
                        : 'text-success'
                    }
                  >
                    {selectedTransaction.fraudScore}%
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <Badge
                    variant={
                      selectedTransaction.status === 'flagged'
                        ? 'destructive'
                        : selectedTransaction.status === 'safe'
                        ? 'default'
                        : 'secondary'
                    }
                  >
                    {selectedTransaction.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Device ID</p>
                  <p className="font-mono text-sm">{selectedTransaction.deviceId}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">IP Address</p>
                  <p className="font-mono text-sm">{selectedTransaction.ipAddress}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Transaction Velocity</p>
                  <p>{selectedTransaction.transactionVelocity} txns/hour</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Payment Method</p>
                  <p>{selectedTransaction.paymentMethod}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Location</p>
                  <p>{selectedTransaction.location}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Timestamp</p>
                  <p>{new Date(selectedTransaction.timestamp).toLocaleString()}</p>
                </div>
              </div>

              {/* Risk Factors */}
              {selectedTransaction.riskFactors.length > 0 && (
                <div>
                  <p className="mb-2">Identified Risk Factors</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedTransaction.riskFactors.map((factor, i) => (
                      <Badge key={i} variant="destructive">
                        {factor}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button variant="outline" className="flex-1">
                  Mark as Safe
                </Button>
                <Button variant="destructive" className="flex-1">
                  Block Transaction
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}