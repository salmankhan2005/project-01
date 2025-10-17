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
  updateProfile: (profileData: any) => Promise<void>;
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
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const response = await apiService.verifyToken();
          setUser(response.user);
          setIsAuthenticated(true);
        } catch (error) {
          localStorage.removeItem('auth_token');
        }
      }
      setIsLoading(false);
    };
    
    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiService.login({ email, password });
    localStorage.setItem('auth_token', response.token);
    setUser(response.user);
    setIsAuthenticated(true);
    setIsGuest(false);
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

  const updateProfile = async (profileData: any) => {
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
