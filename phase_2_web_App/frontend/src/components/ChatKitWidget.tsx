'use client';

/**
 * Simple SSE Chat Widget
 *
 * A custom chat widget that uses Server-Sent Events (SSE) to stream responses
 * from the ChatKit backend. Simpler than the official @openai/chatkit-react widget.
 */

import { useEffect, useState, useRef } from 'react';
import { usePathname } from 'next/navigation';

const ChatKitWidget: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ id: string; role: string; content: string }>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const pathname = usePathname();
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

    try {
      console.log('[ChatKit] Sending message:', userMessage);

      // Call ChatKit endpoint with SSE streaming
      const response = await fetch(`http://localhost:8000/api/v1/chatkit?token=${encodeURIComponent(authToken)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'threads.create',
          params: {
            input: {
              content: [{ type: 'input_text', text: userMessage }]
            }
          }
        }),
      });

      console.log('[ChatKit] Response status:', response.status, response.statusText);

      if (!response.ok) {
        console.error('[ChatKit] Response not OK:', response.status, response.statusText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Read SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      console.log('[ChatKit] Starting to read SSE stream...');

      let buffer = '';
      let currentEvent = '';
      let assistantMessage = '';
      let assistantMsgId = '';
      let chunkCount = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('[ChatKit] Stream ended. Total chunks:', chunkCount);
          break;
        }

        chunkCount++;
        const decodedChunk = decoder.decode(value, { stream: true });
        console.log(`[ChatKit] Chunk ${chunkCount}:`, decodedChunk.substring(0, 200));

        buffer += decodedChunk;
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // keep incomplete line

        console.log(`[ChatKit] Processing ${lines.length} lines from chunk ${chunkCount}`);

        for (const rawLine of lines) {
          const line = rawLine.trim();
          if (!line) continue;

          if (line.startsWith('event:')) {
            currentEvent = line.replace('event:', '').trim();
            console.log('[ChatKit] Event:', currentEvent);
            continue;
          }

          if (line.startsWith('data:')) {
            try {
              const jsonStr = line.replace('data:', '').trim();
              const data = JSON.parse(jsonStr);

              console.log(`[ChatKit ${currentEvent}] Parsed data:`, data);
              console.log('[ChatKit] Has data.item?', !!data.item);
              console.log('[ChatKit] data.item keys:', data.item ? Object.keys(data.item) : 'N/A');

              // Handle assistant message
              if (data.item && data.item.role === 'assistant') {
                console.log('[ChatKit] ✓✓✓ FOUND ASSISTANT MESSAGE ✓✓✓');
                assistantMsgId = data.item.id || `msg_${Date.now()}`;

                const contentParts = data.item.content || [];
                console.log('[ChatKit] content type:', Array.isArray(contentParts) ? 'array' : typeof contentParts);
                console.log('[ChatKit] content parts:', contentParts);

                for (const part of contentParts) {
                  if (part.type === 'text') {
                    const text = part.text || part.value || '';
                    assistantMessage += text;
                    console.log('[ChatKit] ✓ Found text part (length):', text.length);
                  }
                }

                // Add message immediately when found
                if (assistantMessage) {
                  setMessages(prev => {
                    const last = prev[prev.length - 1];
                    if (last?.role === 'assistant' && last.id === assistantMsgId) {
                      return [...prev.slice(0, -1), { ...last, content: assistantMessage }];
                    }
                    return [...prev, { id: assistantMsgId, role: 'assistant', content: assistantMessage }];
                  });
                }
              }

              // Stream complete
              if (currentEvent === 'thread.item.done' || currentEvent === 'response.end' || data.type === 'response.end') {
                console.log('[ChatKit] Stream complete');
              }

              // Handle errors
              if (data.error) {
                assistantMessage = `Error: ${data.error}`;
                assistantMsgId = Date.now().toString();
                setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: assistantMessage }]);
              }

            } catch (e) {
              console.error('[ChatKit] JSON parse error:', e, line);
            }
          }
        }
      }

      // Fallback: if no message was added during the loop
      if (!assistantMessage) {
        console.warn('[ChatKit] No assistant message received');
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'I received your message but had trouble generating a response. Please try again.'
        }]);
      }

    } catch (error) {
      console.error('[ChatKit] Chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, there was an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
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
          title="Chat with AI Assistant"
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

export default ChatKitWidget;
