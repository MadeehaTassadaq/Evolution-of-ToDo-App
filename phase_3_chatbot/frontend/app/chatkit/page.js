'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChatKitProvider, ChatInterface } from '@openai/chatkit-react';

export default function ChatKitPage() {
  const [authToken, setAuthToken] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const router = useRouter();

  // Check for auth token on component mount
  useEffect(() => {
    const token = localStorage.getItem('better-auth-token');
    if (!token) {
      router.push('/login');
      return;
    }
    setAuthToken(token);
    setIsInitialized(true);
  }, [router]);

  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Initializing ChatKit...</p>
        </div>
      </div>
    );
  }

  if (!authToken) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">Authentication required</p>
          <button
            onClick={() => router.push('/login')}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  const chatKitConfig = {
    options: {
      serverUrl: 'ws://localhost:8000/api/chatkit/ws', // Direct connection to backend
      token: authToken,
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">Todo AI Chatbot (ChatKit)</h1>
          <button
            onClick={() => {
              localStorage.removeItem('better-auth-token');
              router.push('/login');
            }}
            className="px-4 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-6 flex flex-col">
        {/* ChatKit Interface */}
        <div className="flex-1 bg-white rounded-lg shadow-md h-[70vh] flex flex-col">
          <ChatKitProvider options={chatKitConfig.options}>
            <ChatInterface />
          </ChatKitProvider>
        </div>
      </main>
    </div>
  );
}