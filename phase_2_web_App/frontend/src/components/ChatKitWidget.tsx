'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { usePathname } from 'next/navigation';

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
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const pathname = usePathname();

  // Check authentication status on component mount
  useEffect(() => {
    const token = localStorage.getItem('better-auth-token');
    setIsAuthenticated(!!token);
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const loadConversationHistory = useCallback(async () => {
    if (!isAuthenticated) {
      setMessages([{ id: 'auth-required', text: 'Please log in to start chatting.', sender: 'system', timestamp: new Date().toISOString() }]);
      return;
    }

    try {
      const token = localStorage.getItem('better-auth-token');
      const apiUrl = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/api/v1/conversations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.conversations.length > 0) {
          // Load latest conversation
          const latestConv = data.conversations[0];
          const msgResponse = await fetch(`${apiUrl}/api/v1/conversations/${latestConv.id}/messages`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (msgResponse.ok) {
            const msgData = await msgResponse.json();
            const formattedMessages = msgData.messages.map((msg: any) => ({
              id: msg.id,
              text: msg.content,
              sender: msg.role === 'user' ? 'user' : 'bot',
              timestamp: msg.timestamp
            }));
            setMessages(formattedMessages);
          }
        } else {
          // No conversations yet, show welcome message
          setMessages([{
            id: 'welcome',
            text: 'Hello! I\'m your AI assistant. How can I help you manage your tasks today?',
            sender: 'bot',
            timestamp: new Date().toISOString()
          }]);
        }
      } else {
        // Show welcome message if no conversations
        setMessages([{
          id: 'welcome',
          text: 'Hello! I\'m your AI assistant. How can I help you manage your tasks today?',
          sender: 'bot',
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
      setMessages([{
        id: 'error',
        text: 'Unable to load conversation history. Starting a new conversation.',
        sender: 'system',
        timestamp: new Date().toISOString()
      }]);
    }
  }, [isAuthenticated]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    if (!isAuthenticated) {
      const userMessage: Message = {
        id: Date.now().toString(),
        text: inputValue,
        sender: 'user',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, userMessage]);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: 'Please log in to continue chatting with the AI assistant.',
        sender: 'system',
        timestamp: new Date().toISOString()
      }]);
      setInputValue('');
      return;
    }

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
      const token = localStorage.getItem('better-auth-token');
      const apiUrl = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  // Don't show the widget on the chatkit page to avoid conflicts
  if (pathname === '/chatkit') {
    return null;
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all z-50"
          aria-label="Open chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-80 h-96 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-50">
          {/* Header */}
          <div className="bg-blue-600 text-white p-3 rounded-t-lg flex justify-between items-center">
            <span className="font-semibold">Todo AI Assistant</span>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setMessages([{
                    id: 'welcome',
                    text: 'Hello! I\'m your AI assistant. How can I help you manage your tasks today?',
                    sender: 'bot',
                    timestamp: new Date().toISOString()
                  }]);
                }}
                className="text-white hover:text-gray-200 focus:outline-none text-sm"
                title="New chat"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
              <button
                onClick={toggleChat}
                className="text-white hover:text-gray-200 focus:outline-none"
                title="Close"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-3 bg-gray-50">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <p className="text-center">Start chatting with your AI assistant!</p>
                {isAuthenticated ? (
                  <p className="mt-1 text-xs text-center">Ask me to manage your tasks</p>
                ) : (
                  <p className="mt-1 text-xs text-center">Log in to unlock full features</p>
                )}
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
                          ? 'bg-blue-500 text-white rounded-tr-none'
                          : message.sender === 'system'
                          ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                          : 'bg-gray-200 text-gray-800 rounded-tl-none'
                      }`}
                    >
                      {message.text}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-200 text-gray-800 rounded-2xl rounded-tl-none px-4 py-2 text-sm">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-2 bg-white">
            <div className="flex">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                onKeyDown={handleKeyDown}
                placeholder={isAuthenticated ? "Ask me to manage your tasks..." : "Log in to chat with AI assistant"}
                className="flex-1 border border-gray-300 rounded-lg p-2 text-sm resize-none h-12 max-h-32"
                rows={1}
                disabled={!isAuthenticated || isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading || !isAuthenticated}
                className={`ml-2 px-4 rounded-lg text-white flex items-center ${
                  inputValue.trim() && isAuthenticated && !isLoading
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
            {!isAuthenticated && (
              <div className="text-xs text-center text-gray-500 mt-1">
                <a href="/login" className="text-blue-600 hover:underline">
                  Log in to unlock full chat features
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ChatKitWidget;