'use client';

/**
 * Official OpenAI ChatKit Widget - Hosted Backend with Client Tools
 *
 * This uses the official @openai/chatkit-react package with OpenAI's HOSTED backend.
 * Custom tool execution is handled via onClientTool callback to our FastAPI backend.
 *
 * =============================================================================
 * ARCHITECTURE:
 * =============================================================================
 *
 * Frontend (ChatKit Widget)
 *     ↓ HTTPS (OpenAI Hosted)
 * OpenAI ChatKit Service (api.openai.com/chatkit/v1)
 *     ↓ onClientTool callback
 * Custom Backend (FastAPI @ http://localhost:7860/api/v1/tools/execute)
 *     ↓
 * PostgreSQL Database (via TodoTools service)
 *
 * =============================================================================
 * ENVIRONMENT SETUP:
 * =============================================================================
 *
 * Set in phase_2_web_App/frontend/.env.local:
 *
 * # ChatKit backend URL (for tool execution only)
 * NEXT_PUBLIC_CHATKIT_BACKEND_URL=http://localhost:7860
 *
 * # OpenAI Domain Key (registered for madeehatassadaq.github.io)
 * NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_699dd137050c8194b8ac6b936da88aa408d6ecf59a4d7a47
 *
 * =============================================================================
 * IMPORTANT: BOTH BACKENDS MUST BE RUNNING:
 * =============================================================================
 *
 * Terminal 1: Phase II Todo Backend (port 8000)
 *   cd phase_2_web_App/backend && python app.py
 *
 * Terminal 2: Phase III ChatBot Backend (port 7860)
 *   cd phase_3_chatbot/backend && python main.py
 *
 * Terminal 3: Frontend (port 3000/3001)
 *   cd phase_2_web_App/frontend && npm run dev
 *
 * =============================================================================
 * HOW IT WORKS:
 * =============================================================================
 *
 * 1. User types message in ChatKit widget
 * 2. Widget sends request to OpenAI's hosted ChatKit service
 * 3. OpenAI processes with AI and determines if tools are needed
 * 4. If tools needed, widget's onClientTool is called
 * 5. onClientTool calls our backend at /api/v1/tools/execute
 * 6. Backend executes tool and returns result
 * 7. Result sent back to OpenAI to format response
 * 8. User sees final response in widget
 *
 * @see https://openai.github.io/chatkit-js/
 */

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { ChatKit, useChatKit } from '@openai/chatkit-react';

// ============================================================================
// ENVIRONMENT CONFIGURATION
// ============================================================================

// Custom ChatKit backend URL (FastAPI + ChatKit Python SDK)
// This is our custom backend - NOT OpenAI's hosted service
const CHATKIT_BACKEND_URL = process.env.NEXT_PUBLIC_CHATKIT_BACKEND_URL || 'http://localhost:7860';

// Full API URL for the ChatKit endpoint
const CHATKIT_API_URL = `${CHATKIT_BACKEND_URL}/api/v1/chatkit`;

// OpenAI Domain Key (registered for madeehatassadaq.github.io)
const CHATKIT_DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || 'domain_pk_699dd137050c8194b8ac6b936da88aa408d6ecf59a4d7a47';

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
  useEffect(() => {
    console.log('[ChatKit Widget] ================================================');
    console.log('[ChatKit Widget] Using OpenAI-Hosted Backend with Client Tools');
    console.log('[ChatKit Widget] Tool Execution Backend:', CHATKIT_BACKEND_URL);
    console.log('[ChatKit Widget] Auth Token:', !!getToken());
    console.log('[ChatKit Widget] Current URL:', typeof window !== 'undefined' ? window.location.origin : 'N/A');
    console.log('[ChatKit Widget] ================================================');
  }, []);

  const chatKit = useChatKit({
    // OpenAI-Hosted Backend Configuration
    // This uses OpenAI's hosted ChatKit service, which handles domain validation
    // Our custom backend is called via onClientTool for tool execution
    api: {
      url: "https://api.openai.com/chatkit/v1",
      domainKey: CHATKIT_DOMAIN_KEY,
    },

    // Client Tool Handler - calls our custom backend for tool execution
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
      console.error('[ChatKit Widget] Error:', error);

      // Check for backend connectivity issues
      if (error.message?.includes('fetch') || error.message?.includes('network')) {
        console.error('[ChatKit Widget] Cannot connect to tool execution backend at:', CHATKIT_BACKEND_URL);
        console.error('[ChatKit Widget] Make sure the backend is running: cd phase_3_chatbot/backend && python main.py');
      }
    },

    // Ready handler
    onReady: () => {
      console.log('[ChatKit Widget] Widget is ready and connected to OpenAI-hosted backend!');
    },
  });

  // Fixed position widget in bottom-right corner
  return (
    <div className="fixed bottom-6 right-6 z-[9999]">
      <ChatKit control={chatKit.control} />
    </div>
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

  if (isAuthPage || !isInitialized || !authToken) {
    return null;
  }

  console.log('[ChatKit Widget] Showing widget');
  return <ChatKitAuthenticatedWidget />;
};

export default ChatKitOfficialWidget;
