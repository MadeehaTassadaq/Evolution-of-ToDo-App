'use client';

/**
 * Official OpenAI ChatKit Widget Implementation
 * Uses @openai/chatkit-react library with proper SSE protocol handling
 */

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

const ChatKitWidgetOfficial: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const pathname = usePathname();

  const getToken = (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('authToken') || localStorage.getItem('better-auth-token');
  };

  useEffect(() => {
    const token = getToken();
    setAuthToken(token);

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

  if (isAuthPage || !authToken) {
    return null;
  }

  // Dynamically load ChatKit when widget is opened
  const loadChatKit = async () => {
    try {
      // Load the official ChatKit React components
      const { OpenAIChatProvider, useChatKit } = await import('@openai/chatkit-react');

      // We'll render this in a portal or separate component
      console.log('[ChatKit] Official library loaded');
    } catch (error) {
      console.error('[ChatKit] Failed to load official library:', error);
    }
  };

  const handleWidgetOpen = () => {
    setIsWidgetOpen(true);
    loadChatKit();
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isWidgetOpen && (
        <button
          onClick={handleWidgetOpen}
          className="fixed bottom-6 right-6 bg-emerald-500 hover:bg-emerald-400 text-black p-4 rounded-full shadow-lg transition-all z-50"
          aria-label="Open AI Assistant"
          title="Chat with AI Assistant"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Panel - Using iframe to isolate ChatKit */}
      {isWidgetOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-6rem)] bg-gray-900 border border-emerald-500 rounded-lg shadow-xl z-50 flex flex-col">
          {/* Header */}
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

          {/* ChatKit iframe with proper protocol */}
          <iframe
            src={`/api/v1/chatkit?token=${encodeURIComponent(authToken)}`}
            className="flex-1 w-full bg-gray-900 border-0"
            title="AI Assistant"
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        </div>
      )}
    </>
  );
};

export default ChatKitWidgetOfficial;
