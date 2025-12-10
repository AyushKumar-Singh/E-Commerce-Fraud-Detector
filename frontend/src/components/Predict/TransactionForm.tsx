import { useState } from 'react';
import { motion } from 'motion/react';
import { CreditCard, DollarSign, Send, AlertTriangle, CheckCircle, Loader2, Zap } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Slider } from '../ui/slider';
import { api } from '../../services/api';
import { toast } from 'sonner';

interface TransactionFormProps {
    onSuccess?: () => void;
    onCancel?: () => void;
}

// Sample fraudulent transaction from Kaggle dataset
const FRAUD_PRESET = {
    Time: 406,
    V1: -2.3122265423263,
    V2: 1.95199201064158,
    V3: -1.60985073229769,
    V4: 3.9979055875468,
    V5: -0.522187864667764,
    V6: -1.42654531920595,
    V7: -2.53738730624579,
    V8: 1.39165724829804,
    V9: -2.77008927719433,
    V10: -2.77227214465915,
    V11: 3.20203320709635,
    V12: -2.89990738849473,
    V13: -0.595221881324605,
    V14: -4.28925378244217,
    V15: 0.389724120274487,
    V16: -1.14074717980657,
    V17: -2.83005567450437,
    V18: -0.0168224681808257,
    V19: 0.416955705037907,
    V20: 0.126910559061474,
    V21: 0.517232370861764,
    V22: -0.0350493686052974,
    V23: -0.465211076182388,
    V24: 0.320198198514526,
    V25: 0.0445191674731724,
    V26: 0.177839798284401,
    V27: 0.261145002567677,
    V28: -0.143275874698919,
    Amount: 0
};

// Sample normal transaction
const NORMAL_PRESET = {
    Time: 0,
    V1: -1.35980713155,
    V2: -0.0727811733098,
    V3: 2.53634673797,
    V4: 1.37815522427,
    V5: -0.338320769942,
    V6: 0.462387777978,
    V7: 0.239598554061,
    V8: 0.0986979012611,
    V9: 0.36378697024,
    V10: 0.0907941719789,
    V11: -0.551599533261,
    V12: -0.617800855762,
    V13: -0.991389847236,
    V14: -0.311169353699,
    V15: 1.46817697209,
    V16: -0.470400525259,
    V17: 0.207971241929,
    V18: 0.0257905801987,
    V19: 0.403992960255,
    V20: 0.251412098239,
    V21: -0.018306777944,
    V22: 0.277837575559,
    V23: -0.110473910188,
    V24: 0.0669280749146,
    V25: 0.128539358274,
    V26: -0.189114843889,
    V27: 0.133558376741,
    V28: -0.0210530534538,
    Amount: 149.62
};

export function TransactionForm({ onSuccess, onCancel }: TransactionFormProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [formData, setFormData] = useState(NORMAL_PRESET);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setResult(null);

        try {
            const response = await api.predictTransactionKaggle(formData);
            setResult(response);

            if (response.decision) {
                toast.error('🚨 Fraudulent Transaction Detected', {
                    description: `Fraud Score: ${(response.score_final * 100).toFixed(1)}%`
                });
            } else {
                toast.success('✓ Transaction appears safe', {
                    description: `Fraud Score: ${(response.score_final * 100).toFixed(1)}%`
                });
            }

            if (onSuccess) {
                setTimeout(onSuccess, 500);
            }
        } catch (error: any) {
            toast.error('Failed to analyze transaction', {
                description: error?.response?.data?.error || 'Connection error'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const applyPreset = (preset: typeof NORMAL_PRESET) => {
        setFormData(preset);
        setResult(null);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Quick Presets */}
                <div className="space-y-2">
                    <Label>Quick Presets (Kaggle Dataset Samples)</Label>
                    <div className="flex flex-wrap gap-2">
                        <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-success/10 gap-2"
                            onClick={() => applyPreset(NORMAL_PRESET)}
                        >
                            <CheckCircle className="h-3 w-3" />
                            Normal Transaction
                        </Badge>
                        <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-destructive/10 gap-2"
                            onClick={() => applyPreset(FRAUD_PRESET)}
                        >
                            <AlertTriangle className="h-3 w-3" />
                            Fraudulent Transaction
                        </Badge>
                    </div>
                </div>

                {/* Amount */}
                <div className="space-y-2">
                    <Label htmlFor="amount" className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4" />
                        Transaction Amount ($)
                    </Label>
                    <Input
                        id="amount"
                        type="number"
                        step="0.01"
                        value={formData.Amount}
                        onChange={(e) => setFormData({ ...formData, Amount: parseFloat(e.target.value) || 0 })}
                        placeholder="149.62"
                    />
                </div>

                {/* Time */}
                <div className="space-y-2">
                    <Label htmlFor="time">Time (seconds since first transaction)</Label>
                    <Input
                        id="time"
                        type="number"
                        value={formData.Time}
                        onChange={(e) => setFormData({ ...formData, Time: parseFloat(e.target.value) || 0 })}
                        placeholder="0"
                    />
                </div>

                {/* PCA Features Preview */}
                <div className="space-y-2">
                    <Label>PCA Features (V1-V28)</Label>
                    <div className="grid grid-cols-4 gap-2 p-3 bg-muted/50 rounded-lg text-xs">
                        {Array.from({ length: 28 }, (_, i) => i + 1).map((i) => {
                            const key = `V${i}` as keyof typeof formData;
                            const value = formData[key] as number;
                            return (
                                <div key={i} className="flex justify-between">
                                    <span className="text-muted-foreground">V{i}:</span>
                                    <span className={Math.abs(value) > 2 ? 'text-destructive font-medium' : ''}>
                                        {value.toFixed(2)}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        These are PCA-transformed features from the Kaggle Credit Card Fraud dataset. Values outside ±2 standard deviations are highlighted.
                    </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                    {onCancel && (
                        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
                            Cancel
                        </Button>
                    )}
                    <Button type="submit" disabled={isLoading} className="flex-1 gap-2">
                        {isLoading ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Zap className="h-4 w-4" />
                                Analyze with CatBoost
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
                                {result.decision ? 'FRAUD Detected' : 'Transaction Safe'}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Transaction ID: {result.transaction_id} • Model: {result.model}
                            </p>
                        </div>
                        <div className="ml-auto text-right">
                            <Badge className="mb-1" variant={result.decision ? 'destructive' : 'default'}>
                                {(result.score_final * 100).toFixed(1)}% Risk
                            </Badge>
                            <p className="text-xs text-muted-foreground">
                                {result.confidence} Confidence
                            </p>
                        </div>
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
