'use client';

/**
 * Official OpenAI ChatKit Widget - Working Implementation
 * Uses @openai/chatkit-react library with proper configuration
 */

import { useEffect, useState, useRef } from 'react';
import { usePathname } from 'next/navigation';
import { useChatKit, ChatKit } from '@openai/chatkit-react';

const DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || 'domain_pk_696a62eeaf508197aedf5220ff381cc906aff41e18fc2ffc';
const SERVER_URL = process.env.NEXT_PUBLIC_CHATKIT_SERVER_URL || 'http://localhost:8000/api/v1/chatkit';

interface ChatKitWidgetProps {
  className?: string;
}

const ChatKitWidgetFixed: React.FC<ChatKitWidgetProps> = ({ className = '' }) => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const pathname = usePathname();
  const chatKitRef = useRef<any>(null);

  // Get authentication token
  const getToken = (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('authToken') || localStorage.getItem('better-auth-token');
  };

  useEffect(() => {
    const token = getToken();
    setAuthToken(token);
    setIsInitialized(true);

    const handleStorageChange = () => setAuthToken(getToken());
    const handleAuthChange = (e: any) => {
      if (e.detail?.token) setAuthToken(e.detail.token);
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('authStateChanged', handleAuthChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authStateChanged', handleAuthChange);
    };
  }, []);

  // Hide on login/register pages
  const isAuthPage = pathname === '/login' || pathname === '/register';

  if (isAuthPage || !isInitialized || !authToken) {
    return null;
  }

  // Internal ChatKit component with proper configuration
  const InternalChatKit = () => {
    const { control } = useChatKit({
      api: {
        url: SERVER_URL,
        domainKey: DOMAIN_KEY,
      },
      theme: {
        colorScheme: 'dark',
        radius: 'soft',
        color: {
          accent: { primary: '#10B981', level: 2 }, // Emerald color
        },
      },
      header: {
        enabled: true,
      },
      history: {
        enabled: false, // Hide thread history for simplicity
      },
      composer: {
        placeholder: 'Ask me about your tasks...',
      },
      onError: ({ error }) => {
        console.error('[ChatKit] Error:', error);
      },
      onLog: ({ name, data }) => {
        console.log('[ChatKit]', name, data);
      },
    });

    return (
      <ChatKit
        ref={chatKitRef}
        control={control}
        className="h-full w-full"
      />
    );
  };

  if (!isWidgetOpen) {
    // Floating button when closed
    return (
      <button
        onClick={() => setIsWidgetOpen(true)}
        className={`fixed bottom-6 right-6 bg-emerald-500 hover:bg-emerald-400 text-black p-4 rounded-full shadow-lg transition-all z-50 ${className}`}
        aria-label="Open AI Assistant"
        title="Chat with AI Assistant"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>
    );
  }

  // Chat panel when open
  return (
    <div className="fixed bottom-6 right-6 w-[400px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-6rem)] bg-gray-900 border border-emerald-500 rounded-lg shadow-xl z-50 flex flex-col">
      {/* Header with close button */}
      <div className="bg-emerald-500 text-black p-4 flex justify-between items-center rounded-t-lg">
        <div className="flex items-center gap-2">
          <span className="font-semibold">🤖 Todo AI Assistant</span>
        </div>
        <button
          onClick={() => setIsWidgetOpen(false)}
          className="text-black hover:text-gray-800 p-1"
          title="Close chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      {/* ChatKit component */}
      <div className="flex-1 overflow-hidden">
        <InternalChatKit />
      </div>
    </div>
  );
};

export default ChatKitWidgetFixed;
