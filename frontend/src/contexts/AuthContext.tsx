import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Types
export interface User {
  user_id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  organization_id: number;
  organization_name: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
  organization_name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  email: string;
  role: string;
  organization: string;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

// Auth Provider Component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        try {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          
          // Verify token is still valid
          const response = await axios.get('/api/auth/verify-token', {
            headers: {
              Authorization: `Bearer ${storedToken}`
            }
          });

          if (!response.data.valid) {
            // Token invalid, clear auth
            clearAuth();
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          clearAuth();
        }
      }
      
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post<AuthResponse>('/api/auth/login', {
        email,
        password
      });

      const { access_token } = response.data;

      // Fetch full user details
      const userResponse = await axios.get<User>('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });

      const userData = userResponse.data;

      // Store auth data
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));

      setToken(access_token);
      setUser(userData);
    } catch (error: any) {
      console.error('Login failed:', error);
      const status = error.response?.status;
      if (status === 429) {
        throw new Error(
          error.response?.data?.error?.message ||
          'Too many login attempts. Please wait 60 seconds and try once.'
        );
      }
      throw new Error(
        error.response?.data?.detail || 'Login failed. Please check your credentials.'
      );
    }
  };

  // Register function
  const register = async (data: RegisterData) => {
    try {
      await axios.post('/api/auth/register', data);

      // After successful registration, automatically log in
      await login(data.email, data.password);
    } catch (error: any) {
      console.error('Registration failed:', error);
      throw new Error(
        error.response?.data?.detail || 'Registration failed. Please try again.'
      );
    }
  };

  // Logout function
  const logout = async () => {
    try {
      if (token) {
        await axios.post('/api/auth/logout', {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      }
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      clearAuth();
    }
  };

  // Refresh user data
  const refreshUser = async () => {
    if (!token) return;

    try {
      const response = await axios.get<User>('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      const userData = response.data;
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      clearAuth();
    }
  };

  // Clear authentication data
  const clearAuth = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
