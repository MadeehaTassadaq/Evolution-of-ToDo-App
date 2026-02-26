'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

const ChatKitWidget: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null); // Store conversation ID for session history
  const pathname = usePathname();

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

  const sendMessage = async () => {
    if (!inputValue.trim() || !authToken) return;

    const userMessage = inputValue;
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Call backend endpoint - use stored conversation_id for session history
      const response = await fetch('http://localhost:7860/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: conversationId, // Use stored conversation_id (null on first message creates new)
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();

      // Store the conversation_id from response for session history
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      // Display the response
      const assistantMessage = data.response || data.message || 'Done!';
      setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }]);

      // If there were tool calls, you could show them as indicators
      if (data.tool_calls && data.tool_calls.length > 0) {
        console.log('Tools used:', data.tool_calls);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, there was an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (pathname === '/chatkit' || !isInitialized || !authToken) return null;

  return (
    <>
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

      {isWidgetOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] h-[600px] bg-black border border-emerald-500 rounded-lg shadow-xl z-50 flex flex-col">
          <div className="bg-emerald-500 text-black p-4 flex justify-between items-center rounded-t-lg">
            <div className="flex items-center gap-2">
              <span className="font-semibold">🤖 Todo AI Assistant</span>
            </div>
            <button onClick={() => setIsWidgetOpen(false)} className="text-black hover:text-gray-800 p-1">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

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
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3 rounded-lg text-sm ${
                  msg.role === 'user' ? 'bg-emerald-500 text-black' : 'bg-gray-800 text-white'
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
