'use client';

/**
 * Official OpenAI ChatKit Widget - Custom Backend with ChatKit Python SDK
 *
 * This uses the official @openai/chatkit-react package with a CUSTOM backend
 * running the ChatKit Python SDK (deployed on Hugging Face Spaces).
 *
 * =============================================================================
 * ARCHITECTURE:
 * =============================================================================
 *
 * Frontend (ChatKit Widget)
 *     ↓ HTTPS/WSS
 * Custom Backend (FastAPI + ChatKit Python SDK @ Hugging Face Spaces)
 *     ↓
 * OpenAI Agents SDK (AI processing + Tool execution)
 *     ↓
 * PostgreSQL Database (via Neon)
 *
 * =============================================================================
 * ENVIRONMENT SETUP:
 * =============================================================================
 *
 * Set in phase_2_web_App/frontend/.env.local:
 *
 * # ChatKit Custom Backend URL (Hugging Face Spaces)
 * # Local development: http://localhost:7860
 * # Production: https://your-space-name.hf.space
 * NEXT_PUBLIC_CHATKIT_BACKEND_URL=http://localhost:7860
 *
 * =============================================================================
 * DEPLOYMENT:
 * =============================================================================
 *
 * For Vercel deployment:
 * 1. Deploy backend to Hugging Face Spaces
 * 2. Set NEXT_PUBLIC_CHATKIT_BACKEND_URL to your Hugging Face Space URL
 * 3. NO domain key needed (custom backend handles authentication)
 *
 * @see https://github.com/openai/chatkit-python
 */

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { ChatKit, useChatKit } from '@openai/chatkit-react';

// ============================================================================
// ENVIRONMENT CONFIGURATION
// ============================================================================

// Custom ChatKit backend URL (FastAPI + ChatKit Python SDK)
// This is our custom backend - NOT OpenAI's hosted service
// For local: http://localhost:7860
// For Hugging Face Spaces: https://madeeha123-fastapi.hf.space (configured in Vercel)
// Use Phase II backend URL instead of Phase III
const CHATKIT_BACKEND_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8000';

// Helper to get auth token and build URL with query parameter
const getChatKitApiUrl = (): string => {
  const token = getToken();
  const baseUrl = `${CHATKIT_BACKEND_URL}/api/v1/chatkit`;
  if (token) {
    return `${baseUrl}?token=${encodeURIComponent(token)}`;
  }
  return baseUrl;
};

// Domain Key for ChatKit widget (required for domain validation)
// For local development, we may need to skip domain validation or use a test key
// For production: Use your registered domain key
const isLocalhost = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1'
);

// For local development, you can either:
// 1. Use a test domain key that includes localhost
// 2. Skip domain validation (not recommended for production)
const CHATKIT_DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || (
  isLocalhost ? undefined : 'domain_pk_696a62eeaf508197aedf5220ff381cc906aff41e18fc2ffc'
);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('authToken') || localStorage.getItem('better-auth-token');
};

const getInitialThreadId = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('chatkit_thread_id');
};

// ============================================================================
// CHATKIT WIDGET COMPONENT
// ============================================================================

/**
 * Inner component that only renders when authenticated
 */
function ChatKitAuthenticatedWidget() {
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);

  useEffect(() => {
    console.log('[ChatKit Widget] ================================================');
    console.log('[ChatKit Widget] Using Custom Backend (ChatKit Python SDK)');
    console.log('[ChatKit Widget] Backend URL:', getChatKitApiUrl());
    console.log('[ChatKit Widget] Auth Token:', !!getToken());
    console.log('[ChatKit Widget] Current URL:', typeof window !== 'undefined' ? window.location.origin : 'N/A');
    console.log('[ChatKit Widget] Domain Key:', CHATKIT_DOMAIN_KEY?.substring(0, 20) + '...' || 'None (local development)');
    console.log('[ChatKit Widget] ================================================');

    // Test backend connection
    const testBackendConnection = async () => {
      try {
        const response = await fetch(`${CHATKIT_BACKEND_URL}/health`);
        if (response.ok) {
          console.log('[ChatKit Widget] ✅ Backend is reachable!');
        } else {
          console.warn('[ChatKit Widget] ⚠️ Backend returned non-OK status:', response.status);
        }
      } catch (error) {
        console.error('[ChatKit Widget] ❌ Backend is NOT reachable:', error);
      }
    };

    testBackendConnection();
  }, []);

  const chatKit = useChatKit({
    // Custom Backend Configuration (ChatKit Python SDK on Hugging Face Spaces)
    // This uses our custom backend running the ChatKit Python SDK
    // The backend handles AI processing and tool execution server-side
    api: {
      url: getChatKitApiUrl(), // Dynamic URL with auth token as query parameter
      domainKey: CHATKIT_DOMAIN_KEY,
    },

    // Trigger task list refresh after assistant responses
    onResponseEnd: async () => {
      console.log('[ChatKit Widget] Response ended, triggering task list refresh...');
      // Dispatch custom event to notify task list component
      window.dispatchEvent(new CustomEvent('chatkit-operation-complete', {
        detail: { timestamp: Date.now() }
      }));
    },

    // Client Tool Handler - NOT NEEDED with custom backend
    // The ChatKit Python SDK backend handles tool execution server-side
    // Kept for compatibility but won't be called with custom backend
    onClientTool: async (invocation: { name: string; params: Record<string, unknown> }) => {
      console.log('[ChatKit Widget] Client tool invocation:', invocation);

      const token = getToken();
      if (!token) {
        console.error('[ChatKit Widget] No auth token available for tool execution');
        return { success: false, error: 'Not authenticated' };
      }

      try {
        // Call our custom backend's tool execution endpoint
        const response = await fetch(`${CHATKIT_BACKEND_URL}/api/v1/tools/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: invocation.name,
            arguments: invocation.params,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: response.statusText }));
          console.error('[ChatKit Widget] Tool execution failed:', errorData);
          return { success: false, error: errorData.error || 'Tool execution failed' };
        }

        const result = await response.json();
        console.log('[ChatKit Widget] Tool execution result:', result);
        return result;

      } catch (error) {
        console.error('[ChatKit Widget] Tool execution error:', error);
        return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
      }
    },

    // Thread persistence
    initialThread: getInitialThreadId(),
    onThreadChange: (event: { threadId: string | null }) => {
      const newThreadId = event.threadId;
      if (newThreadId) {
        localStorage.setItem('chatkit_thread_id', newThreadId);
      } else {
        localStorage.removeItem('chatkit_thread_id');
      }
    },

    // Theme customization
    theme: 'dark',

    // Header configuration
    header: {
      enabled: true,
      title: {
        enabled: true,
        text: '🤖 Todo AI Assistant',
      },
    },

    // Start screen with suggested prompts
    startScreen: {
      greeting: 'Hi! I can help you manage your todos. What would you like to do?',
      prompts: [
        { label: 'Add a new task', prompt: 'Add a new task', icon: 'write' },
        { label: 'Show my tasks', prompt: 'Show all my tasks', icon: 'search' },
        { label: 'Mark task complete', prompt: 'Mark a task as complete', icon: 'sparkle' },
      ],
    },

    // Input placeholder
    composer: {
      placeholder: 'Ask me anything about your todos...',
    },

    // Error handler
    onError: ({ error }) => {
      console.error('[ChatKit Widget] ================================================');
      console.error('[ChatKit Widget] ERROR:', error);
      console.error('[ChatKit Widget] Error name:', error.name);
      console.error('[ChatKit Widget] Error message:', error.message);
      console.error('[ChatKit Widget] Error stack:', error.stack);
      console.error('[ChatKit Widget] Backend URL:', getChatKitApiUrl());
      console.error('[ChatKit Widget] Domain Key:', CHATKIT_DOMAIN_KEY?.substring(0, 20) + '...');
      console.error('[ChatKit Widget] ================================================');

      // Check for backend connectivity issues
      if (error.message?.includes('fetch') || error.message?.includes('network')) {
        console.error('[ChatKit Widget] Cannot connect to ChatKit backend at:', getChatKitApiUrl());
        console.error('[ChatKit Widget] Make sure the backend is running and accessible');
      }
    },

    // Ready handler
    onReady: () => {
      console.log('[ChatKit Widget] Widget is ready and connected to custom backend!');

      // Debug: Check if ChatKit element is in DOM
      setTimeout(() => {
        const chatkitElements = document.querySelectorAll('openai-chatkit, [data-chatkit], .chatkit-widget');
        console.log('[ChatKit Widget] Debug - ChatKit elements found:', chatkitElements.length);
        chatkitElements.forEach((el, i) => {
          console.log(`[ChatKit Widget] Debug - Element ${i}:`, {
            tagName: el.tagName,
            className: el.className,
            id: el.id,
            display: window.getComputedStyle(el).display,
            visibility: window.getComputedStyle(el).visibility,
            opacity: window.getComputedStyle(el).opacity,
            zIndex: window.getComputedStyle(el).zIndex,
          });
        });

        // Check all fixed positioned elements
        const fixedElements = Array.from(document.querySelectorAll('*')).filter(
          el => window.getComputedStyle(el).position === 'fixed'
        );
        console.log('[ChatKit Widget] Debug - Fixed positioned elements:', fixedElements.length);
        const bottomRightElements = fixedElements.filter(el => {
          const style = window.getComputedStyle(el);
          return style.bottom.includes('rem') || style.bottom.includes('px');
        });
        console.log('[ChatKit Widget] Debug - Bottom-right positioned elements:', bottomRightElements.map(el => ({
          tagName: el.tagName,
          className: el.className,
          bottom: window.getComputedStyle(el).bottom,
          right: window.getComputedStyle(el).right,
        })));
      }, 1000);
    },
  });

  // Fixed position widget in bottom-right corner
  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsWidgetOpen(!isWidgetOpen)}
        className="fixed bottom-6 right-6 z-[9999] w-14 h-14 bg-green-500 hover:bg-green-600 text-white rounded-full shadow-lg flex items-center justify-center text-2xl transition-all duration-200 hover:scale-110 active:scale-95"
        title={isWidgetOpen ? "Close AI Assistant" : "Open AI Assistant"}
        style={{
          boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)',
        }}
      >
        {isWidgetOpen ? '✕' : '🤖'}
      </button>

      {/* ChatKit Widget Panel (shown when open) */}
      {isWidgetOpen && (
        <div className="fixed bottom-24 right-6 z-[9998] w-[400px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-6rem)]">
          <ChatKit control={chatKit.control} className="h-full w-full" />
        </div>
      )}
    </>
  );
}

// ============================================================================
// MAIN WIDGET COMPONENT (handles auth state)
// ============================================================================

/**
 * Main widget component that handles authentication state
 */
const ChatKitOfficialWidget: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const pathname = usePathname();

  // Auto-initialize after 1 second
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      console.log('[ChatKit Widget] Initialization timeout - forcing initialized=true');
      setIsInitialized(true);
    }, 1000);
    return () => clearTimeout(timeoutId);
  }, []);

  // Initialize and listen for auth changes
  useEffect(() => {
    const checkToken = () => {
      const token = getToken();
      console.log('[ChatKit Widget] Token check:', !!token);
      if (token) {
        console.log('[ChatKit Widget] Token (first 20 chars):', token.substring(0, 20) + '...');
      }
      setAuthToken(token);
      setIsInitialized(true);
    };

    // Initial check
    checkToken();

    // Listen for auth changes
    const handleStorageChange = () => checkToken();
    const handleAuthChange = (e: any) => {
      console.log('[ChatKit Widget] Auth state changed:', e.detail);
      checkToken();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('authStateChanged', handleAuthChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authStateChanged', handleAuthChange);
    };
  }, []);

  // Hide on login/register pages
  const isAuthPage = pathname === '/login' || pathname === '/register' || pathname === '/chatkit';

  // Debug logging
  console.log('[ChatKit Widget] Render state:', {
    pathname,
    isAuthPage,
    isInitialized,
    hasAuthToken: !!authToken,
    tokenPrefix: authToken ? authToken.substring(0, 20) + '...' : 'none'
  });

  if (isAuthPage || !isInitialized || !authToken) {
    console.log('[ChatKit Widget] Not showing widget because:', {
      reason: isAuthPage ? 'auth page' : !isInitialized ? 'not initialized' : 'no auth token'
    });
    return null;
  }

  console.log('[ChatKit Widget] Showing widget');
  return <ChatKitAuthenticatedWidget />;
};

export default ChatKitOfficialWidget;
