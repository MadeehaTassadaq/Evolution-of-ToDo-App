'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  isAuthenticated: boolean;
  userId: string | null;
  login: (token: string, userId: string) => void;
  logout: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const router = useRouter();

  // Check for existing token on mount
  useEffect(() => {
    const token = getStoredToken();
    const storedUserId = localStorage.getItem('userId');

    if (token) {
      setIsAuthenticated(true);
      setUserId(storedUserId);
    }
  }, []);

  const getStoredToken = (): string | null => {
    // Check both localStorage and cookies for token
    let token = localStorage.getItem('authToken');
    if (!token) {
      // Try to get from cookies
      const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('authToken='))
        ?.split('=')[1];
      if (cookieValue) {
        token = cookieValue;
        // Store in localStorage for API calls
        localStorage.setItem('authToken', cookieValue);
      }
    }
    return token;
  };

  const login = (token: string, userId: string) => {
    // Store in both localStorage and cookies
    localStorage.setItem('authToken', token);
    document.cookie = `authToken=${token}; path=/; max-age=86400; SameSite=Strict`;

    localStorage.setItem('userId', userId);
    document.cookie = `userId=${userId}; path=/; max-age=86400; SameSite=Strict`;

    setIsAuthenticated(true);
    setUserId(userId);
  };

  const logout = () => {
    // Clear both localStorage and cookies
    document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
    document.cookie = 'userId=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';

    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');

    setIsAuthenticated(false);
    setUserId(null);
    router.push('/login');
  };

  const getToken = () => {
    return getStoredToken();
  };

  return (
    <AuthContext.Provider value={{
      isAuthenticated,
      userId,
      login,
      logout,
      getToken
    }}>
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