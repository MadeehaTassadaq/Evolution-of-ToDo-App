'use client';

/**
 * Official OpenAI ChatKit Widget
 *
 * This component uses the official @openai/chatkit-react package
 * to integrate with your custom backend that uses OpenAI Agents SDK.
 *
 * Architecture:
 * Frontend (ChatKit) → Your Backend (FastAPI) → OpenAI Agents SDK → Tools
 *
 * No workflowId required - we're using Custom Backend Mode.
 */

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';

const ChatKitOfficialWidget: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const pathname = usePathname();

  // Backend configuration
  const CHATKIT_SERVER_URL = process.env.NEXT_PUBLIC_CHATKIT_URL || 'http://localhost:7860';
  const SESSION_ENDPOINT = `${CHATKIT_SERVER_URL}/api/v1/chatkit/session`;

  const getToken = (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('authToken') || localStorage.getItem('better-auth-token');
  };

  // Initialize ChatKit when component mounts
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsInitialized(true);
      return;
    }

    setAuthToken(token);
    setIsInitialized(true);

    // Listen for auth changes
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

  // Create ChatKit session when widget opens
  const createSession = async (): Promise<string | null> => {
    if (!authToken) return null;

    try {
      const response = await fetch(SESSION_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          thread_id: threadId, // Resume existing thread if available
        }),
      });

      if (!response.ok) {
        console.error('Failed to create ChatKit session');
        return null;
      }

      const data = await response.json();

      // Store thread_id for session continuity
      if (data.thread_id && !threadId) {
        setThreadId(data.thread_id);
      }

      return data.client_secret;
    } catch (error) {
      console.error('Error creating ChatKit session:', error);
      return null;
    }
  };

  // Hide on login page or if not initialized
  if (pathname === '/chatkit' || !isInitialized || !authToken) return null;

  return (
    <>
      {/* Chat Toggle Button */}
      {!isWidgetOpen && (
        <button
          onClick={() => setIsWidgetOpen(true)}
          className="fixed bottom-6 right-6 bg-emerald-500 hover:bg-emerald-400 text-black p-4 rounded-full shadow-lg transition-all z-50 hover:scale-110"
          aria-label="Open AI Assistant"
          title="Chat with AI Assistant"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Widget Container */}
      {isWidgetOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] h-[600px] bg-black border border-emerald-500 rounded-lg shadow-xl z-50 flex flex-col">
          {/* Header */}
          <div className="bg-emerald-500 text-black p-4 flex justify-between items-center rounded-t-lg">
            <div className="flex items-center gap-2">
              <span className="font-semibold">🤖 Todo AI Assistant</span>
              <span className="text-xs bg-black/20 px-2 py-1 rounded">Powered by OpenAI</span>
            </div>
            <button
              onClick={() => setIsWidgetOpen(false)}
              className="text-black hover:text-gray-800 p-1 hover:bg-black/10 rounded"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Chat Interface - Using Official ChatKit */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {typeof window !== 'undefined' && (
              <ChatKitChatPanel
                serverUrl={CHATKIT_SERVER_URL}
                authToken={authToken}
                threadId={threadId}
                onThreadIdChange={setThreadId}
              />
            )}
          </div>
        </div>
      )}
    </>
  );
};

/**
 * ChatKit Chat Panel Component
 *
 * This component handles the actual ChatKit integration.
 * It loads the ChatKit library dynamically and sets up the connection.
 */
function ChatKitChatPanel({
  serverUrl,
  authToken,
  threadId,
  onThreadIdChange
}: {
  serverUrl: string;
  authToken: string;
  threadId: string | null;
  onThreadIdChange: (id: string) => void;
}) {
  const [messages, setMessages] = useState<Array<{role: string; content: string}>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Load conversation history when thread changes
  useEffect(() => {
    if (!threadId || !authToken) return;

    const loadHistory = async () => {
      try {
        const response = await fetch(`${serverUrl}/api/v1/conversations/${threadId}/messages`, {
          headers: { 'Authorization': `Bearer ${authToken}` },
        });

        if (response.ok) {
          const data = await response.json();
          const history = (data.messages || []).map((msg: any) => ({
            role: msg.role,
            content: msg.content,
          }));
          setMessages(history);
        } else {
          // If conversation not found or permission denied, start fresh
          console.log('Could not load conversation history, starting fresh');
          setMessages([]);
        }
      } catch (err) {
        console.error('Failed to load history:', err);
        // On error, just start fresh without showing an error
        setMessages([]);
      }
    };

    loadHistory();
  }, [threadId, authToken, serverUrl]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (ws) ws.close();
    };
  }, [ws]);

  const sendMessage = async () => {
    if (!inputValue.trim() || !authToken) return;

    const userMessage = inputValue;
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      // Use REST API for simplicity (WebSocket is also available)
      const response = await fetch(`${serverUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: threadId,
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();

      // Update thread_id if new conversation was created
      if (data.conversation_id && !threadId) {
        onThreadIdChange(data.conversation_id);
      }

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response || 'Done!'
      }]);

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error. Please try again.'
      }]);
    }
  };

  return (
    <>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-10 text-sm">
            <p className="mb-2">👋 Hello! I'm your AI Todo Assistant.</p>
            <p className="text-xs">Try saying:</p>
            <ul className="text-xs mt-2 space-y-1 text-left inline-block">
              <li>"Add a task to buy groceries"</li>
              <li>"Show me all my tasks"</li>
              <li>"Complete task 1"</li>
              <li>"Delete the completed tasks"</li>
            </ul>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-lg text-sm ${
              msg.role === 'user'
                ? 'bg-emerald-500 text-black'
                : 'bg-gray-800 text-white border border-gray-700'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-white p-3 rounded-lg text-sm">
              ⏳ Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-emerald-500">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message..."
            className="flex-1 bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:border-emerald-500 focus:outline-none text-sm"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="bg-emerald-500 text-black px-4 py-2 rounded-lg hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </>
  );
}

export default ChatKitOfficialWidget;
