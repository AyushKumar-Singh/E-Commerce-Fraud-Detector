import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  loginWithSecret: (secret: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for existing token on mount
    const savedToken = localStorage.getItem('api_token');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
    } else {
      // Auto-login for development (REMOVE IN PRODUCTION)
      const devToken = 'devtoken';
      localStorage.setItem('api_token', devToken);
      setToken(devToken);
      setIsAuthenticated(true);
    }

    // Listen for storage events (logout from other tabs or API interceptor)
    const handleStorageChange = () => {
      const currentToken = localStorage.getItem('api_token');
      if (!currentToken && isAuthenticated) {
        setToken(null);
        setIsAuthenticated(false);
      } else if (currentToken && !isAuthenticated) {
        setToken(currentToken);
        setIsAuthenticated(true);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [isAuthenticated]);

  const login = (newToken: string) => {
    localStorage.setItem('api_token', newToken);
    setToken(newToken);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('api_token');
    setToken(null);
    setIsAuthenticated(false);
  };

  const loginWithSecret = async (secret: string) => {
    const response = await api.login(secret);
    login(response.token);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, login, logout, loginWithSecret }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
