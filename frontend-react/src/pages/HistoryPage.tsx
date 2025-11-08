import React, { useState } from 'react';
import { useRecentFlags } from '@/hooks/useFraudStats';
import { Card } from '@/components/common/Card';
import { Loader2, MessageSquare, CreditCard } from 'lucide-react';
import clsx from 'clsx';
import { format } from 'date-fns';

type HistoryType = 'review' | 'transaction';

export const HistoryPage: React.FC = () => {
  const [type, setType] = useState<HistoryType>('review');
  const { data, isLoading } = useRecentFlags(type);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Prediction History</h1>
        <p className="mt-2 text-gray-600">View all flagged items</p>
      </div>

      {/* Type Selector */}
      <div className="flex gap-4">
        <button
          onClick={() => setType('review')}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
            type === 'review'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          )}
        >
          <MessageSquare className="h-5 w-5" />
          Reviews
        </button>
        <button
          onClick={() => setType('transaction')}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
            type === 'transaction'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          )}
        >
          <CreditCard className="h-5 w-5" />
          Transactions
        </button>
      </div>

      {/* Items List */}
      <Card>
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {data?.items.map((item) => (
              <div key={item.id} className="py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      {type === 'review' ? 'Review' : 'Transaction'} #{item.id}
                    </span>
                    <span className="ml-3 text-sm text-gray-500">
                      User {item.user_id}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-danger-50 text-danger-700 rounded-full text-sm font-semibold">
                      {(item.score * 100).toFixed(0)}% fraud
                    </span>
                    <span className="text-sm text-gray-500">
                      {format(new Date(item.created_at), 'MMM d, yyyy HH:mm')}
                    </span>
                  </div>
                </div>

                {type === 'review' && item.text && (
                  <p className="text-sm text-gray-700 mb-2">{item.text}</p>
                )}

                {type === 'transaction' && item.amount && (
                  <p className="text-sm text-gray-700 mb-2">
                    Amount: <span className="font-semibold">₹{item.amount.toLocaleString()}</span>
                  </p>
                )}

                {item.reasons.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {item.reasons.map((reason, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded"
                      >
                        {reason}
                      </span>
                    ))}
                  </div>
                )}

                {item.ip && (
                  <p className="mt-2 text-xs text-gray-500">
                    IP: <code className="bg-gray-100 px-1 py-0.5 rounded">{item.ip}</code>
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};