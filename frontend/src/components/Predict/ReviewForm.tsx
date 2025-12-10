import { useState } from 'react';
import { motion } from 'motion/react';
import { MessageSquare, Star, Send, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { api } from '../../services/api';
import { toast } from 'sonner';

interface ReviewFormProps {
    onSuccess?: () => void;
    onCancel?: () => void;
}

export function ReviewForm({ onSuccess, onCancel }: ReviewFormProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<any>(null);

    const [formData, setFormData] = useState({
        user_id: 1,
        product_id: 'PROD-001',
        review_text: '',
        rating: 5,
        ip_address: '192.168.1.1',
        device_fingerprint: 'demo-device-001'
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setResult(null);

        try {
            const response = await api.predictReview(formData);
            setResult(response);

            if (response.decision) {
                toast.error('⚠️ Review flagged as FAKE', {
                    description: `Fraud Score: ${(response.score_final * 100).toFixed(1)}%`
                });
            } else {
                toast.success('✓ Review appears genuine', {
                    description: `Fraud Score: ${(response.score_final * 100).toFixed(1)}%`
                });
            }

            // Refresh the reviews list
            if (onSuccess) {
                setTimeout(onSuccess, 500);
            }
        } catch (error: any) {
            toast.error('Failed to submit review', {
                description: error?.response?.data?.error || 'Connection error'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const setRating = (rating: number) => {
        setFormData({ ...formData, rating });
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* User and Product IDs */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label htmlFor="user_id">User ID</Label>
                        <Input
                            id="user_id"
                            type="number"
                            value={formData.user_id}
                            onChange={(e) => setFormData({ ...formData, user_id: parseInt(e.target.value) || 1 })}
                            placeholder="1"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="product_id">Product ID</Label>
                        <Input
                            id="product_id"
                            value={formData.product_id}
                            onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                            placeholder="PROD-001"
                        />
                    </div>
                </div>

                {/* Rating */}
                <div className="space-y-2">
                    <Label>Rating</Label>
                    <div className="flex items-center gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                            <button
                                key={star}
                                type="button"
                                onClick={() => setRating(star)}
                                className="p-1 hover:scale-110 transition-transform"
                            >
                                <Star
                                    className={`h-6 w-6 transition-colors ${star <= formData.rating
                                            ? 'fill-warning text-warning'
                                            : 'fill-muted text-muted-foreground'
                                        }`}
                                />
                            </button>
                        ))}
                        <span className="ml-2 text-muted-foreground text-sm">
                            {formData.rating} star{formData.rating !== 1 ? 's' : ''}
                        </span>
                    </div>
                </div>

                {/* Review Text */}
                <div className="space-y-2">
                    <Label htmlFor="review_text">Review Text</Label>
                    <Textarea
                        id="review_text"
                        value={formData.review_text}
                        onChange={(e) => setFormData({ ...formData, review_text: e.target.value })}
                        placeholder="Write your review here... (Try suspicious patterns like 'AMAZING! BEST EVER! BUY NOW!')"
                        rows={4}
                        required
                    />
                    <p className="text-xs text-muted-foreground">
                        Tips: Excessive enthusiasm, ALL CAPS, multiple exclamation marks, and generic praise often indicate fake reviews.
                    </p>
                </div>

                {/* Quick Presets */}
                <div className="space-y-2">
                    <Label>Quick Presets</Label>
                    <div className="flex flex-wrap gap-2">
                        <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-success/10"
                            onClick={() => setFormData({
                                ...formData,
                                review_text: "I've been using this product for about a month now. It does what it says, though the build quality could be better. Delivery was on time. Overall satisfied with my purchase.",
                                rating: 4
                            })}
                        >
                            Genuine Review
                        </Badge>
                        <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-destructive/10"
                            onClick={() => setFormData({
                                ...formData,
                                review_text: "AMAZING PRODUCT!!! BEST PURCHASE EVER!!! EVERYONE SHOULD BUY THIS NOW!!! 5 STARS!!! ABSOLUTELY INCREDIBLE!!! MUST HAVE!!!",
                                rating: 5
                            })}
                        >
                            Suspicious Review
                        </Badge>
                        <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-warning/10"
                            onClick={() => setFormData({
                                ...formData,
                                review_text: "Great product great product great product. Best best best. Very good very good. Recommend recommend recommend.",
                                rating: 5
                            })}
                        >
                            Repetitive Pattern
                        </Badge>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                    {onCancel && (
                        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
                            Cancel
                        </Button>
                    )}
                    <Button type="submit" disabled={isLoading || !formData.review_text} className="flex-1 gap-2">
                        {isLoading ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Send className="h-4 w-4" />
                                Submit & Analyze
                            </>
                        )}
                    </Button>
                </div>
            </form>

            {/* Result Display */}
            {result && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className={`rounded-lg border p-4 ${result.decision
                            ? 'border-destructive/50 bg-destructive/5'
                            : 'border-success/50 bg-success/5'
                        }`}
                >
                    <div className="flex items-center gap-3 mb-3">
                        {result.decision ? (
                            <AlertTriangle className="h-6 w-6 text-destructive" />
                        ) : (
                            <CheckCircle className="h-6 w-6 text-success" />
                        )}
                        <div>
                            <p className={result.decision ? 'text-destructive' : 'text-success'}>
                                {result.decision ? 'FAKE Review Detected' : 'Review Appears Genuine'}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Review ID: {result.review_id}
                            </p>
                        </div>
                        <Badge className="ml-auto" variant={result.decision ? 'destructive' : 'default'}>
                            {(result.score_final * 100).toFixed(1)}% Risk
                        </Badge>
                    </div>

                    {result.reasons && result.reasons.length > 0 && (
                        <div className="space-y-2">
                            <p className="text-sm text-muted-foreground">Risk Factors:</p>
                            <div className="flex flex-wrap gap-2">
                                {result.reasons.map((reason: string, i: number) => (
                                    <Badge key={i} variant="secondary" className="text-xs">
                                        {reason}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    )}
                </motion.div>
            )}
        </motion.div>
    );
}
