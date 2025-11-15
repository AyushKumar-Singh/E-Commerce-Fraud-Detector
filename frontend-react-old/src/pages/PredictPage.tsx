import React, { useState } from 'react';
import { ReviewForm } from '@/components/Predict/ReviewForm';
import { TransactionForm } from '@/components/Predict/TransactionForm';
import { Shield, CreditCard, MessageSquare } from 'lucide-react';
import clsx from 'clsx';

type Tab = 'review' | 'transaction';

export const PredictPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('review');

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Fraud Prediction</h1>
        <p className="mt-2 text-gray-600">Analyze reviews and transactions in real-time</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('review')}
            className={clsx(
              'flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === 'review'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <MessageSquare className="h-5 w-5" />
            Review Analysis
          </button>
          <button
            onClick={() => setActiveTab('transaction')}
            className={clsx(
              'flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === 'transaction'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <CreditCard className="h-5 w-5" />
            Transaction Analysis
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-8">
        {activeTab === 'review' ? <ReviewForm /> : <TransactionForm />}
      </div>
    </div>
  );
};