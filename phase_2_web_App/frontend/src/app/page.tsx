'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // Wait for auth state to be determined before redirecting
    if (typeof window !== 'undefined') {
      // Check if we have an auth token in localStorage or cookies
      let token = localStorage.getItem('authToken');
      if (!token) {
        // Try to get from cookies as fallback
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

      if (token) {
        router.replace('/tasks');
      } else {
        router.replace('/login');
      }
    }
  }, []); // Run only once on mount

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="flex items-center gap-3">
        <svg className="animate-spin w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span className="text-gray-400">Loading...</span>
      </div>
    </div>
  );
}
