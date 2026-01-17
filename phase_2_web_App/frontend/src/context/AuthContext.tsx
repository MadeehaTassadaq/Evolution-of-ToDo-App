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

    // Only update state if we have a token, otherwise maintain default state (false)
    if (token) {
      setIsAuthenticated(true);
      setUserId(storedUserId);
    } else {
      setIsAuthenticated(false);
      setUserId(null);
    }
  }, []);

  const getStoredToken = (): string | null => {
    // Prioritize cookies over localStorage for consistency
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.trim().startsWith('authToken='))
      ?.split('=')[1];

    if (cookieValue) {
      // Ensure token is also in localStorage for API calls
      if (typeof window !== 'undefined') {
        localStorage.setItem('authToken', cookieValue);
      }
      return cookieValue;
    }

    // Fallback to localStorage if cookies are not available
    if (typeof window !== 'undefined') {
      return localStorage.getItem('authToken');
    }

    return null;
  };

  const login = (token: string, userId: string) => {
    // Store in both localStorage and cookies
    localStorage.setItem('authToken', token);
    // Also store as better-auth-token for compatibility with Phase 3 chatbot
    localStorage.setItem('better-auth-token', token);

    // For Vercel deployment, use Secure flag if on HTTPS (production)
    const isSecure = typeof window !== 'undefined' && window.location.protocol === 'https:';
    document.cookie = `authToken=${token}; path=/; max-age=86400; SameSite=Lax${isSecure ? '; Secure' : ''}`;
    document.cookie = `better-auth-token=${token}; path=/; max-age=86400; SameSite=Lax${isSecure ? '; Secure' : ''}`;

    localStorage.setItem('userId', userId);
    document.cookie = `userId=${userId}; path=/; max-age=86400; SameSite=Lax${isSecure ? '; Secure' : ''}`;

    setIsAuthenticated(true);
    setUserId(userId);

    // Dispatch custom event for ChatKitWidget and other components to react to auth changes
    window.dispatchEvent(new CustomEvent('authStateChanged', { detail: { isAuthenticated: true, token } }));
  };

  const logout = () => {
    // Clear both localStorage and cookies
    document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';
    document.cookie = 'better-auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';
    document.cookie = 'userId=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';

    localStorage.removeItem('authToken');
    localStorage.removeItem('better-auth-token');
    localStorage.removeItem('userId');

    setIsAuthenticated(false);
    setUserId(null);

    // Dispatch custom event for ChatKitWidget and other components to react to auth changes
    window.dispatchEvent(new CustomEvent('authStateChanged', { detail: { isAuthenticated: false, token: null } }));

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