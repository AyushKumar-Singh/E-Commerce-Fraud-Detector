import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from 'frontend/src/services/api';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Card } from '@/components/common/Card';
import { ReviewPayload, ReviewPrediction } from '@/types';
import { AlertTriangle, CheckCircle, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

export const ReviewForm: React.FC = () => {
  const [formData, setFormData] = useState<ReviewPayload>({
    user_id: 0,
    product_id: '',
    review_text: '',
    rating: 5,
  });

  const [result, setResult] = useState<ReviewPrediction | null>(null);

  const mutation = useMutation({
    mutationFn: (data: ReviewPayload) => api.predictReview(data),
    onSuccess: (data) => {
      setResult(data);
      toast.success('Prediction complete!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Prediction failed');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Form */}
      <Card title="Check Review for Fraud">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="User ID"
            type="number"
            name="user_id"
            value={formData.user_id || ''}
            onChange={handleChange}
            required
            placeholder="123"
          />

          <Input
            label="Product ID"
            type="text"
            name="product_id"
            value={formData.product_id}
            onChange={handleChange}
            required
            placeholder="PROD-456"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Review Text
            </label>
            <textarea
              name="review_text"
              value={formData.review_text}
              onChange={handleChange}
              required
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter review text..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rating: {formData.rating}
            </label>
            <input
              type="range"
              name="rating"
              min="1"
              max="5"
              value={formData.rating}
              onChange={handleChange}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1⭐</span>
              <span>2⭐</span>
              <span>3⭐</span>
              <span>4⭐</span>
              <span>5⭐</span>
            </div>
          </div>

          <Input
            label="IP Address (Optional)"
            type="text"
            name="ip_address"
            value={formData.ip_address || ''}
            onChange={handleChange}
            placeholder="192.168.1.1"
          />

          <Button type="submit" loading={mutation.isPending} className="w-full">
            <Shield className="mr-2 h-5 w-5" />
            Analyze Review
          </Button>
        </form>
      </Card>

      {/* Result */}
      {result && (
        <Card title="Analysis Result">
          <div className="space-y-6">
            {/* Decision Badge */}
            <div className="text-center">
              {result.decision ? (
                <div className="inline-flex items-center gap-2 px-6 py-3 bg-danger-50 text-danger-700 rounded-full">
                  <AlertTriangle className="h-6 w-6" />
                  <span className="font-bold text-lg">FAKE REVIEW DETECTED</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 px-6 py-3 bg-success-50 text-success-700 rounded-full">
                  <CheckCircle className="h-6 w-6" />
                  <span className="font-bold text-lg">GENUINE REVIEW</span>
                </div>
              )}
            </div>

            {/* Confidence */}
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Confidence Level</p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
                <span className="text-2xl font-bold text-gray-900 uppercase">{result.confidence}</span>
              </div>
            </div>

            {/* Scores */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-600">Final Score</span>
                <span className="text-lg font-bold text-gray-900">
                  {(result.score_final * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 rounded-full transition-all duration-500"
                  style={{
                    width: `${result.score_final * 100}%`,
                    backgroundColor: result.decision ? 'rgb(239, 68, 68)' : 'rgb(16, 185, 129)',
                  }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs text-gray-600">Model Score</p>
                  <p className="text-lg font-bold text-blue-600">
                    {(result.score_model * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <p className="text-xs text-gray-600">Rules Boost</p>
                  <p className="text-lg font-bold text-purple-600">
                    +{(result.score_rules * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Reasons */}
            {result.reasons.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Detection Reasons</h4>
                <ul className="space-y-2">
                  {result.reasons.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className="text-danger-500 mt-0.5">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Metadata */}
            <div className="pt-4 border-t border-gray-200 text-xs text-gray-500">
              <p>Review ID: {result.review_id}</p>
              <p>Threshold: {(result.threshold * 100).toFixed(0)}%</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};