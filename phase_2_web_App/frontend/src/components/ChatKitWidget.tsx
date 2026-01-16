'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';

// Define a simple ChatKit-like interface since we're connecting to our existing backend
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot' | 'system';
  timestamp: string;
}

const ChatKitWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const pathname = usePathname();

  // Check for auth token on component mount
  useEffect(() => {
    const tokenFromLocalStorage = localStorage.getItem('authToken') ?? null;
    const tokenFromBetterAuth = localStorage.getItem('better-auth-token') ?? null;
    const tokenFromCookies = document.cookie
      .split('; ')
      .find(row => row.trim().startsWith('authToken='))
      ?.split('=')[1] ?? null;

    const token = tokenFromLocalStorage || tokenFromBetterAuth || tokenFromCookies;

    setAuthToken(token);
    setIsInitialized(true);
  }, []);

  // Don't show the widget on the chatkit page to avoid conflicts
  if (pathname === '/chatkit' || !isInitialized) {
    return null;
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || !authToken) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(process.env.NEXT_PUBLIC_CHATBOT_API_URL + '/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          message: inputValue,
          conversation_id: messages.length > 0 ? messages[0].id : null
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.response,
          sender: 'bot',
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorData = await response.json();
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: `Sorry, I encountered an error: ${errorData.detail || 'Unable to process your request'}`,
          sender: 'system',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I\'m having trouble connecting. Please try again.',
        sender: 'system',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && authToken && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-green-500 text-black p-4 rounded-full shadow-lg hover:bg-green-400 transition-all z-50"
          aria-label="Open chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Widget with black and green theme */}
      {isOpen && authToken && (
        <div className="fixed bottom-6 right-6 w-80 h-96 bg-black border border-green-500 rounded-lg shadow-xl flex flex-col z-50">
          {/* Header */}
          <div className="bg-green-500 text-black p-3 rounded-t-lg flex justify-between items-center">
            <span className="font-semibold">Todo AI Assistant</span>
            <button
              onClick={() => setIsOpen(false)}
              className="text-black hover:text-gray-800 focus:outline-none"
              title="Close"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-3 bg-gray-900">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-green-400 text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <p className="text-center">Start chatting with your AI assistant!</p>
                <p className="mt-1 text-xs text-center">Ask me to manage your tasks</p>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                        message.sender === 'user'
                          ? 'bg-green-500 text-black rounded-tr-none'
                          : message.sender === 'system'
                          ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                          : 'bg-gray-700 text-green-300 rounded-tl-none'
                      }`}
                    >
                      {message.text}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-700 text-green-300 rounded-2xl rounded-tl-none px-4 py-2 text-sm">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-green-500 p-2 bg-black">
            <div className="flex">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me to manage your tasks..."
                className="flex-1 bg-gray-800 text-white border border-green-500 rounded-lg p-2 text-sm resize-none h-12 max-h-32"
                rows={1}
                disabled={!authToken || isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading || !authToken}
                className={`ml-2 px-4 rounded-lg text-black flex items-center ${
                  inputValue.trim() && authToken && !isLoading
                    ? 'bg-green-500 hover:bg-green-400'
                    : 'bg-gray-600 cursor-not-allowed'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatKitWidget;