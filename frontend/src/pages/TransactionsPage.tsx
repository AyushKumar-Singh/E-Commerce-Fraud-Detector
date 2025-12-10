import { motion } from 'motion/react';
import { useState } from 'react';
import { ArrowUpDown, Filter, Search, Plus, RefreshCcw, CheckCircle, AlertTriangle, Zap } from 'lucide-react';
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { useAllTransactions } from '../hooks/useAPI';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { useDebounce } from '../hooks/useDebounce';
import { TransactionForm } from '../components/Predict/TransactionForm';
import { useQueryClient } from '@tanstack/react-query';

export function TransactionsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'amount' | 'fraudScore' | 'timestamp'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<any | null>(null);

  const queryClient = useQueryClient();
  const { data, isLoading, refetch, isRefetching } = useAllTransactions(1, 100, filterType);
  const debouncedSearch = useDebounce(searchQuery, 300);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const transactions = data?.items || [];
  const total = data?.total || 0;

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
      if (sortBy === 'fraudScore') return ((a.score || 0) - (b.score || 0)) * multiplier;
      return (new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime()) * multiplier;
    });

  // Calculate stats
  const fraudCount = transactions.filter(t => t.is_fraud).length;
  const safeCount = transactions.filter(t => !t.is_fraud).length;
  const totalAmount = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
  const fraudAmount = transactions.filter(t => t.is_fraud).reduce((sum, t) => sum + (t.amount || 0), 0);

  const toggleSort = (field: 'amount' | 'fraudScore' | 'timestamp') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['allTransactions'] });
    refetch();
  };

  const handleAddSuccess = () => {
    setIsAddDialogOpen(false);
    handleRefresh();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <div className="flex items-center justify-between">
          <div>
            <h2>Transaction Monitoring</h2>
            <p className="text-muted-foreground">
              CatBoost ML model trained on Kaggle Credit Card Fraud Detection dataset
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={handleRefresh}
              disabled={isRefetching}
            >
              <RefreshCcw className={`h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
            </Button>
            <Button onClick={() => setIsAddDialogOpen(true)} className="gap-2">
              <Plus className="h-4 w-4" />
              Add Transaction
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-4">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-1">
                <p className="text-muted-foreground text-sm">Total Transactions</p>
                <p className="text-2xl font-bold">{total}</p>
                <p className="text-xs text-muted-foreground">${totalAmount.toFixed(2)}</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.15 }}
        >
          <Card className="border-success/30">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-success" />
                <div>
                  <p className="text-muted-foreground text-sm">Safe</p>
                  <p className="text-2xl font-bold text-success">{safeCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-destructive/30">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                <div>
                  <p className="text-muted-foreground text-sm">Fraudulent</p>
                  <p className="text-2xl font-bold text-destructive">{fraudCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.25 }}
        >
          <Card className="border-warning/30">
            <CardContent className="pt-6">
              <div className="space-y-1">
                <p className="text-muted-foreground text-sm">Amount at Risk</p>
                <p className="text-2xl font-bold text-warning">${fraudAmount.toFixed(2)}</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

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
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Transactions</SelectItem>
                    <SelectItem value="fraud">Fraudulent Only</SelectItem>
                    <SelectItem value="safe">Safe Only</SelectItem>
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
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
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
                    <TableHead>Channel</TableHead>
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
                  {filteredTransactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-12 text-muted-foreground">
                        No transactions found. Click "Add Transaction" to test the CatBoost model.
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredTransactions.map((txn, index) => (
                      <motion.tr
                        key={txn.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.03 }}
                        className="cursor-pointer hover:bg-accent/5"
                        onClick={() => setSelectedTransaction(txn)}
                      >
                        <TableCell className="font-medium">TXN-{txn.id}</TableCell>
                        <TableCell className="text-muted-foreground">USR-{txn.user_id}</TableCell>
                        <TableCell>${(txn.amount || 0).toFixed(2)}</TableCell>
                        <TableCell>
                          <span
                            className={
                              (txn.score || 0) > 0.7
                                ? 'text-destructive'
                                : (txn.score || 0) > 0.4
                                  ? 'text-warning'
                                  : 'text-success'
                            }
                          >
                            {((txn.score || 0) * 100).toFixed(0)}%
                          </span>
                        </TableCell>
                        <TableCell>
                          <Badge variant={txn.is_fraud ? 'destructive' : 'default'}>
                            {txn.is_fraud ? 'fraud' : 'safe'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{txn.channel || 'N/A'}</TableCell>
                        <TableCell className="text-muted-foreground">
                          {txn.created_at
                            ? new Date(txn.created_at).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                            : 'N/A'}
                        </TableCell>
                      </motion.tr>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Add Transaction Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Analyze Transaction with CatBoost
            </DialogTitle>
            <DialogDescription>
              Test the fraud detection model using sample transactions from the Kaggle Credit Card Fraud dataset.
              The model uses 30 PCA-transformed features to detect anomalous patterns.
            </DialogDescription>
          </DialogHeader>
          <TransactionForm
            onSuccess={handleAddSuccess}
            onCancel={() => setIsAddDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Transaction Detail Modal */}
      <Dialog open={!!selectedTransaction} onOpenChange={() => setSelectedTransaction(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Transaction Analysis Details</DialogTitle>
            <DialogDescription>
              Detailed fraud analysis for transaction {selectedTransaction?.id}
            </DialogDescription>
          </DialogHeader>
          {selectedTransaction && (
            <div className="space-y-4">
              {/* Status Badge */}
              <div className={`rounded-lg p-4 ${selectedTransaction.is_fraud ? 'bg-destructive/10 border-destructive/30' : 'bg-success/10 border-success/30'
                } border`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {selectedTransaction.is_fraud ? (
                      <AlertTriangle className="h-6 w-6 text-destructive" />
                    ) : (
                      <CheckCircle className="h-6 w-6 text-success" />
                    )}
                    <div>
                      <p className={`font-bold ${selectedTransaction.is_fraud ? 'text-destructive' : 'text-success'}`}>
                        {selectedTransaction.is_fraud ? 'FRAUDULENT' : 'SAFE'}
                      </p>
                      <p className="text-muted-foreground text-sm">CatBoost Analysis</p>
                    </div>
                  </div>
                  <Badge variant={selectedTransaction.is_fraud ? 'destructive' : 'default'} className="text-lg px-4 py-2">
                    {((selectedTransaction.score || 0) * 100).toFixed(1)}% Risk
                  </Badge>
                </div>
              </div>

              {/* Transaction Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-muted-foreground text-sm">Transaction ID</p>
                  <p className="font-medium">TXN-{selectedTransaction.id}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-sm">User ID</p>
                  <p className="font-medium">USR-{selectedTransaction.user_id}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-sm">Amount</p>
                  <p className="font-medium">${(selectedTransaction.amount || 0).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-sm">Channel</p>
                  <p className="font-medium">{selectedTransaction.channel || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-sm">IP Address</p>
                  <p className="font-medium font-mono text-sm">{selectedTransaction.ip || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-sm">Timestamp</p>
                  <p className="font-medium">
                    {selectedTransaction.created_at ? new Date(selectedTransaction.created_at).toLocaleString() : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Risk Factors */}
              {selectedTransaction.reasons && selectedTransaction.reasons.length > 0 && (
                <div>
                  <p className="font-medium mb-2">Identified Risk Factors</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedTransaction.reasons.map((factor: string, i: number) => (
                      <Badge key={i} variant="destructive">
                        {factor}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button variant="outline" className="flex-1" onClick={() => setSelectedTransaction(null)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}