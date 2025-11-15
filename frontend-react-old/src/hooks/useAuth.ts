import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      isAuthenticated: false,
      login: (token: string) => {
        localStorage.setItem('api_token', token);
        set({ token, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('api_token');
        set({ token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);