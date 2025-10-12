import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, User, LoginData, RegisterData } from '@/services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  isGuest: boolean;
  user: User | null;
  loading: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  continueAsGuest: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      apiService.verifyToken()
        .then(response => {
          setUser(response.user);
          setIsAuthenticated(true);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (data: LoginData) => {
    const response = await apiService.login(data);
    localStorage.setItem('token', response.token);
    setUser(response.user);
    setIsAuthenticated(true);
    setIsGuest(false);
  };

  const register = async (data: RegisterData) => {
    const response = await apiService.register(data);
    localStorage.setItem('token', response.token);
    setUser(response.user);
    setIsAuthenticated(true);
    setIsGuest(false);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setIsGuest(false);
  };

  const continueAsGuest = () => {
    setIsGuest(true);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isGuest, user, loading, login, register, logout, continueAsGuest }}>
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
