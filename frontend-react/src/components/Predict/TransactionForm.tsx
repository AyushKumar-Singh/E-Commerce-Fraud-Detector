import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from 'frontend/src/services/api';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Card } from '@/components/common/Card';
import { TransactionPayload, TransactionPrediction } from '@/types';
import { AlertTriangle, CheckCircle, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';

export const TransactionForm: React.FC = () => {
  const [formData, setFormData] = useState<TransactionPayload>({
    user_id: 0,
    amount: 0,
    currency: 'INR',
    channel: 'web',
  });

  const [result, setResult] = useState<TransactionPrediction | null>(null);

  const mutation = useMutation({
    mutationFn: (data: TransactionPayload) => api.predictTransaction(data),
    onSuccess: (data) => {
      setResult(data);
      toast.success('Transaction analyzed!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Analysis failed');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Form */}
      <Card title="Check Transaction for Fraud">
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
            label="Transaction Amount"
            type="number"
            name="amount"
            step="0.01"
            value={formData.amount || ''}
            onChange={handleChange}
            required
            placeholder="5000.00"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Currency
            </label>
            <select
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="INR">INR (₹)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Channel
            </label>
            <select
              name="channel"
              value={formData.channel}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="web">Web</option>
              <option value="app">Mobile App</option>
              <option value="api">API</option>
              <option value="pos">Point of Sale</option>
            </select>
          </div>

          <Input
            label="IP Address (Optional)"
            type="text"
            name="ip_address"
            value={formData.ip_address || ''}
            onChange={handleChange}
            placeholder="192.168.1.1"
          />

          <Input
            label="Device Fingerprint (Optional)"
            type="text"
            name="device_fingerprint"
            value={formData.device_fingerprint || ''}
            onChange={handleChange}
            placeholder="abc123xyz"
          />

          <Button type="submit" loading={mutation.isPending} className="w-full">
            <DollarSign className="mr-2 h-5 w-5" />
            Analyze Transaction
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
                  <span className="font-bold text-lg">FRAUDULENT TRANSACTION</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 px-6 py-3 bg-success-50 text-success-700 rounded-full">
                  <CheckCircle className="h-6 w-6" />
                  <span className="font-bold text-lg">LEGITIMATE TRANSACTION</span>
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

            {/* Score */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-600">Fraud Score</span>
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
            </div>

            {/* Reasons */}
            {result.reasons.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Risk Factors</h4>
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

            {/* Amount Display */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Transaction Amount</p>
              <p className="text-2xl font-bold text-gray-900">
                {formData.currency === 'INR' && '₹'}
                {formData.currency === 'USD' && '$'}
                {formData.currency === 'EUR' && '€'}
                {formData.currency === 'GBP' && '£'}
                {Number(formData.amount).toLocaleString()}
              </p>
            </div>

            {/* Metadata */}
            <div className="pt-4 border-t border-gray-200 text-xs text-gray-500">
              <p>Transaction ID: {result.transaction_id}</p>
              <p>Channel: {formData.channel}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};