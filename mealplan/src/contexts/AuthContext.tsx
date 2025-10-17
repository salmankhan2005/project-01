import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '@/services/api';

interface User {
  id: string;
  email: string;
  name?: string;
  phone?: string;
  location?: string;
  bio?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isGuest: boolean;
  isSubscribed: boolean;
  isLoading: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  updateProfile: (profileData: Partial<User>) => Promise<void>;
  logout: () => void;
  continueAsGuest: () => void;
  subscribe: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const initializeAuth = async () => {
      // First check if backend is available
      try {
        const isHealthy = await apiService.checkHealth();
        if (!isHealthy) {
          console.warn('Backend server is not available, continuing in guest mode');
          setIsGuest(true);
          setIsLoading(false);
          return;
        }
      } catch (error) {
        console.warn('Health check failed, continuing in guest mode', error);
        setIsGuest(true);
        setIsLoading(false);
        return;
      }
      
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const response = await apiService.verifyToken();
          setUser(response.user);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Token verification failed:', error);
          localStorage.removeItem('auth_token');
        }
      }
      setIsLoading(false);
    };
    
    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiService.login({ email, password });
      localStorage.setItem('auth_token', response.token);
      setUser(response.user);
      setIsAuthenticated(true);
      setIsGuest(false);
    } catch (error) {
      if (error instanceof Error && error.message.includes('Cannot connect to server')) {
        throw new Error('Cannot connect to server. Would you like to continue as a guest?');
      }
      throw error;
    }
  };

  const register = async (email: string, password: string) => {
    const response = await apiService.register({ email, password });
    localStorage.setItem('auth_token', response.token);
    setUser(response.user);
    setIsAuthenticated(true);
    setIsGuest(false);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setIsAuthenticated(false);
    setIsGuest(false);
  };

  const continueAsGuest = () => {
    setIsGuest(true);
    setIsAuthenticated(false);
  };

  const updateProfile = async (profileData: Partial<User>) => {
    const response = await apiService.updateProfile(profileData);
    setUser(response.user);
  };

  const subscribe = () => {
    setIsSubscribed(true);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isGuest, isSubscribed, isLoading, user, login, register, updateProfile, logout, continueAsGuest, subscribe }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
