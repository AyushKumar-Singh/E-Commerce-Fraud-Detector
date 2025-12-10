import { motion } from 'motion/react';
import { useState } from 'react';
import { MessageSquare, Search, Star, Plus, RefreshCcw, CheckCircle, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { useAllReviews } from '../hooks/useAPI';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { useDebounce } from '../hooks/useDebounce';
import { Progress } from '../components/ui/progress';
import { ReviewForm } from '../components/Predict/ReviewForm';
import { useQueryClient } from '@tanstack/react-query';

export function ReviewsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  const queryClient = useQueryClient();
  const { data, isLoading, refetch, isRefetching } = useAllReviews(1, 100, filterType);
  const debouncedSearch = useDebounce(searchQuery, 300);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const reviews = data?.items || [];
  const total = data?.total || 0;

  // Filter reviews by search
  const filteredReviews = reviews.filter((review) => {
    const matchesSearch =
      (review.text || '').toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      review.id.toString().toLowerCase().includes(debouncedSearch.toLowerCase());
    return matchesSearch;
  });

  // Calculate stats
  const fakeCount = reviews.filter(r => r.is_fake).length;
  const genuineCount = reviews.filter(r => !r.is_fake).length;
  const fakePercentage = reviews.length > 0 ? (fakeCount / reviews.length * 100).toFixed(1) : '0';
  const genuinePercentage = reviews.length > 0 ? (genuineCount / reviews.length * 100).toFixed(1) : '0';

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['allReviews'] });
    refetch();
  };

  const handleAddSuccess = () => {
    setIsAddDialogOpen(false);
    handleRefresh();
  };

  return (
    <div className="space-y-6">
      {/* Header with Add Button */}
      <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <div className="flex items-center justify-between">
          <div>
            <h2>Review Analysis</h2>
            <p className="text-muted-foreground">
              NLP-based sentiment analysis for fake review detection using behavioral features
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
              Add Review
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-muted-foreground">Total Reviews</p>
                  <Badge variant="secondary">{total}</Badge>
                </div>
                <p className="text-2xl font-bold">{reviews.length}</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-success/30">
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-success" />
                    <p className="text-muted-foreground">Genuine Reviews</p>
                  </div>
                  <Badge variant="default" className="bg-success">{genuinePercentage}%</Badge>
                </div>
                <p className="text-2xl font-bold text-success">{genuineCount}</p>
                <Progress value={parseFloat(genuinePercentage)} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="border-destructive/30">
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-destructive" />
                    <p className="text-muted-foreground">Fake Reviews</p>
                  </div>
                  <Badge variant="destructive">{fakePercentage}%</Badge>
                </div>
                <p className="text-2xl font-bold text-destructive">{fakeCount}</p>
                <Progress value={parseFloat(fakePercentage)} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search reviews..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Filter */}
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Reviews</SelectItem>
                  <SelectItem value="genuine">Genuine Only</SelectItem>
                  <SelectItem value="fake">Fake Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Reviews List */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Reviews ({filteredReviews.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredReviews.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No reviews found</p>
                  <p className="text-sm">Click "Add Review" to test the fraud detection</p>
                </div>
              ) : (
                filteredReviews.map((review, index) => (
                  <motion.div
                    key={review.id}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.6 + index * 0.05 }}
                    className="rounded-lg border border-border p-4 hover:bg-accent/5 transition-colors space-y-3"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${review.is_fake ? 'bg-destructive/10' : 'bg-success/10'
                          }`}>
                          <MessageSquare className={`h-5 w-5 ${review.is_fake ? 'text-destructive' : 'text-success'
                            }`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-semibold">REV-{review.id}</p>
                            <Badge variant={review.is_fake ? 'destructive' : 'default'}>
                              {review.is_fake ? 'Fake' : 'Genuine'}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              AI Analyzed
                            </Badge>
                          </div>
                          <div className="flex items-center gap-3 text-muted-foreground mt-1">
                            <div className="flex items-center gap-1">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-3 w-3 ${i < (review.rating || 0)
                                      ? 'fill-warning text-warning'
                                      : 'fill-muted text-muted'
                                    }`}
                                />
                              ))}
                            </div>
                            <span>•</span>
                            <span>{review.created_at ? new Date(review.created_at).toLocaleDateString() : 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Fraud Score</p>
                        <p className={`text-lg font-bold ${review.is_fake ? 'text-destructive' : 'text-success'}`}>
                          {((review.score || 0) * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>

                    <p className="text-muted-foreground leading-relaxed pl-13">
                      {review.text || 'No review text available'}
                    </p>

                    <div className="flex items-center justify-between pl-13">
                      <div className="flex items-center gap-4 text-muted-foreground text-sm">
                        <span>Product: {review.product_id || 'N/A'}</span>
                        <span>•</span>
                        <span>User: {review.user_id}</span>
                      </div>
                    </div>

                    {review.reasons && review.reasons.length > 0 && (
                      <div className="pl-13 flex flex-wrap gap-2 items-center">
                        <span className="text-muted-foreground text-sm">
                          {review.is_fake ? 'Suspicious Patterns:' : 'Confidence Factors:'}
                        </span>
                        {review.reasons.map((pattern, i) => (
                          <Badge key={i} variant={review.is_fake ? 'destructive' : 'secondary'} className="text-xs">
                            {pattern}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Add Review Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Add Review for Analysis
            </DialogTitle>
            <DialogDescription>
              Submit a review to test the NLP-based fake review detection model.
              Use the presets to see how the model handles different patterns.
            </DialogDescription>
          </DialogHeader>
          <ReviewForm
            onSuccess={handleAddSuccess}
            onCancel={() => setIsAddDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}