import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Card } from '@/components/common/Card';
import { Shield, Lock } from 'lucide-react';
import toast from 'react-hot-toast';

export const LoginPage: React.FC = () => {
  const [secret, setSecret] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: (secret: string) => api.login(secret),
    onSuccess: (data) => {
      login(data.token);
      toast.success('Login successful!');
      navigate('/');
    },
    onError: () => {
      toast.error('Invalid credentials');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(secret);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-500 rounded-full mb-4">
            <Shield className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Fraud Detector</h1>
          <p className="mt-2 text-gray-600">AI-Powered Fraud Detection System</p>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Input
                label="Admin Secret"
                type="password"
                value={secret}
                onChange={(e) => setSecret(e.target.value)}
                placeholder="Enter admin secret"
                required
              />
              <p className="mt-2 text-xs text-gray-500">
                Default: Use the ADMIN_SECRET from your .env file
              </p>
            </div>

            <Button type="submit" loading={mutation.isPending} className="w-full">
              <Lock className="mr-2 h-5 w-5" />
              Sign In
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              For demo purposes, you can also use API token: <code className="bg-gray-100 px-2 py-1 rounded">devtoken</code>
            </p>
          </div>
        </Card>

        <p className="mt-8 text-center text-sm text-gray-600">
          Protected by enterprise-grade security
        </p>
      </div>
    </div>
  );
};