import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/common/Button';
import { Shield, LogOut, User } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary-500" />
              <span className="text-xl font-bold text-gray-900">Fraud Detector</span>
            </Link>
          </div>

          {/* Navigation */}
          {isAuthenticated && (
            <div className="flex items-center gap-6">
              <Link
                to="/"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/predict"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Predict
              </Link>
              <Link
                to="/history"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                History
              </Link>

              <div className="flex items-center gap-3 ml-6 pl-6 border-l border-gray-200">
                <div className="flex items-center gap-2">
                  <User className="h-5 w-5 text-gray-400" />
                  <span className="text-sm text-gray-600">Admin</span>
                </div>
                <Button variant="secondary" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};