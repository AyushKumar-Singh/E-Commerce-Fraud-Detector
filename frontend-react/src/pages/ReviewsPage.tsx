import { motion } from 'motion/react';
import { useState } from 'react';
import { MessageSquare, Search, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { useRecentFlags } from '../hooks/useAPI';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { useDebounce } from '../hooks/useDebounce';
import { Progress } from '../components/ui/progress';

export function ReviewsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');

  const { data, isLoading } = useRecentFlags('review', 100);
  const debouncedSearch = useDebounce(searchQuery, 300);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const reviews = data?.items || [];

  // Filter reviews
  const filteredReviews = reviews.filter((review) => {
    const matchesSearch =
      (review.text || '').toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      review.id.toString().toLowerCase().includes(debouncedSearch.toLowerCase());
    return matchesSearch;
  });

  // Calculate sentiment stats
  const sentimentCounts = {
    Positive: 0,
    Neutral: 0,
    Fake: reviews.length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <h2>Review Analysis</h2>
        <p className="text-muted-foreground">
          NLP-based sentiment analysis for fake review detection using behavioral features
        </p>
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
                  <p className="text-muted-foreground">Fake Reviews</p>
                  <Badge variant="destructive">
                    {reviews.length > 0 ? '100' : '0'}%
                  </Badge>
                </div>
                <p className="text-destructive">{sentimentCounts.Fake}</p>
                <Progress
                  value={100}
                  className="h-2"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-muted-foreground">Neutral Reviews</p>
                  <Badge variant="secondary">
                    {reviews.length > 0 ? ((sentimentCounts.Neutral / reviews.length) * 100).toFixed(0) : '0'}%
                  </Badge>
                </div>
                <p className="text-muted-foreground">{sentimentCounts.Neutral}</p>
                <Progress
                  value={reviews.length > 0 ? (sentimentCounts.Neutral / reviews.length) * 100 : 0}
                  className="h-2"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-muted-foreground">Fake Reviews</p>
                  <Badge variant="destructive">
                    {reviews.length > 0 ? ((sentimentCounts.Fake / reviews.length) * 100).toFixed(0) : '0'}%
                  </Badge>
                </div>
                <p className="text-destructive">{sentimentCounts.Fake}</p>
                <Progress
                  value={reviews.length > 0 ? (sentimentCounts.Fake / reviews.length) * 100 : 0}
                  className="h-2"
                />
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

              {/* Sentiment Filter */}
              <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by sentiment" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sentiments</SelectItem>
                  <SelectItem value="Positive">Positive</SelectItem>
                  <SelectItem value="Neutral">Neutral</SelectItem>
                  <SelectItem value="Fake">Fake</SelectItem>
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
              {filteredReviews.map((review, index) => (
                <motion.div
                  key={review.id}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="rounded-lg border border-border p-4 hover:bg-accent/5 transition-colors space-y-3"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-destructive/10">
                        <MessageSquare className="h-5 w-5 text-destructive" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p>REV-{review.id}</p>
                          <Badge variant="destructive">
                            Fake
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            AI Detected
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3 text-muted-foreground mt-1">
                          <div className="flex items-center gap-1">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`h-3 w-3 ${
                                  i < (review.rating || 0)
                                    ? 'fill-warning text-warning'
                                    : 'fill-muted text-muted'
                                }`}
                              />
                            ))}
                          </div>
                          <span>•</span>
                          <span>{new Date(review.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-muted-foreground">Fraud Score</p>
                      <p className="text-destructive">
                        {(review.score * 100).toFixed(1)}%
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
                        Suspicious Patterns:
                      </span>
                      {review.reasons.map((pattern, i) => (
                        <Badge key={i} variant="destructive" className="text-xs">
                          {pattern}
                        </Badge>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}