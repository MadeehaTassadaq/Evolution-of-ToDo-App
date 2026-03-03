'use client';

/**
 * Simple Chat Widget - Works with existing Phase II backend
 * Direct fetch with SSE streaming - no external ChatKit library
 */

import { useEffect, useState, useRef } from 'react';
import { usePathname } from 'next/navigation';

const ChatKitWidgetSimple: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ id: string; role: string; content: string }>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const pathname = usePathname();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

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

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || !authToken) return;

    const userMessage = inputValue;
    const userMsgId = Date.now().toString();
    setInputValue('');
    setMessages(prev => [...prev, { id: userMsgId, role: 'user', content: userMessage }]);
    setIsLoading(true);

    // Cancel any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/chatkit?token=${encodeURIComponent(authToken)}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'threads.create',
            params: {
              input: {
                content: [{ type: 'input_text', text: userMessage }]
              }
            }
          }),
          signal: abortControllerRef.current.signal
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let assistantMessage = '';
      let assistantMsgId = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          if (trimmed.startsWith('data:')) {
            try {
              const jsonStr = trimmed.replace('data:', '').trim();
              const data = JSON.parse(jsonStr);

              console.log('[ChatKit Simple] Received:', data);

              // Handle thread.item.added event
              if (data.item && data.item.role === 'assistant') {
                assistantMsgId = data.item.id;
                const content = data.item.content || [];

                for (const part of content) {
                  if (part.type === 'text' && part.text) {
                    assistantMessage = part.text;

                    // Update message immediately
                    setMessages(prev => {
                      const exists = prev.find(m => m.id === assistantMsgId);
                      if (exists) {
                        return prev.map(m =>
                          m.id === assistantMsgId
                            ? { ...m, content: assistantMessage }
                            : m
                        );
                      }
                      return [...prev, {
                        id: assistantMsgId,
                        role: 'assistant',
                        content: assistantMessage
                      }];
                    });
                  }
                }
              }
            } catch (e) {
              console.error('[ChatKit Simple] Parse error:', e);
            }
          }
        }
      }

      // Fallback if no message was added
      if (!assistantMessage) {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'I received your message. How can I help with your tasks?'
        }]);
      }

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('[ChatKit Simple] Request cancelled');
      } else {
        console.error('[ChatKit Simple] Error:', error);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Sorry, there was an error. Please try again.'
        }]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  // Hide on login/register pages
  const isAuthPage = pathname === '/login' || pathname === '/register';

  if (isAuthPage || !isInitialized || !authToken) {
    return null;
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isWidgetOpen && (
        <button
          onClick={() => setIsWidgetOpen(true)}
          className="fixed bottom-6 right-6 bg-emerald-500 hover:bg-emerald-400 text-black p-4 rounded-full shadow-lg transition-all z-50"
          aria-label="Open AI Assistant"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Panel */}
      {isWidgetOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-6rem)] bg-gray-900 border border-emerald-500 rounded-lg shadow-xl z-50 flex flex-col">
          {/* Header */}
          <div className="bg-emerald-500 text-black p-4 flex justify-between items-center rounded-t-lg">
            <span className="font-semibold">🤖 Todo AI Assistant</span>
            <button
              onClick={() => setIsWidgetOpen(false)}
              className="text-black hover:text-gray-800 p-1"
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-10 text-sm">
                <p className="mb-2">👋 Hello! I'm your AI Todo Assistant.</p>
                <p>Try saying:</p>
                <ul className="text-xs mt-2 space-y-1 text-left inline-block">
                  <li>"Add a task to buy groceries"</li>
                  <li>"Show me all my tasks"</li>
                  <li>"Complete task 1"</li>
                </ul>
              </div>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-lg text-sm whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-emerald-500 text-black'
                      : 'bg-gray-800 text-white'
                  }`}
                >
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
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-emerald-500 rounded-b-lg">
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
                className="bg-emerald-500 text-black px-4 py-2 rounded-lg hover:bg-emerald-400 disabled:opacity-50 text-sm font-medium"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatKitWidgetSimple;
