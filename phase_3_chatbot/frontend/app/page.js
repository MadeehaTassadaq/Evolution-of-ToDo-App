'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const router = useRouter();

  // Check for auth token on component mount
  useEffect(() => {
    const token = localStorage.getItem('better-auth-token');
    if (!token) {
      router.push('/login');
      return;
    }
    setAuthToken(token);
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !authToken) return;

    // Add user message to UI immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Prepare the request body
      const requestBody = {
        message: input
      };

      // Include conversation ID if we have one
      if (conversationId) {
        requestBody.conversation_id = conversationId;
      }

      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(requestBody)
      });

      if (response.status === 401) {
        // Token expired or invalid, redirect to login
        localStorage.removeItem('better-auth-token');
        router.push('/login');
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update conversation ID from response
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        tool_calls: data.tool_calls || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">Todo AI Chatbot</h1>
          <button
            onClick={() => {
              localStorage.removeItem('better-auth-token');
              router.push('/login');
            }}
            className="px-4 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-6 flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 bg-white rounded-lg shadow-md mb-4 h-[60vh] overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to Todo AI Chatbot!</h2>
              <p className="text-gray-600">
                I can help you manage your tasks. Try asking me to add, list, update, or complete tasks.
              </p>
              <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm text-gray-700">
                <p className="font-medium mb-2">Examples:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>"Add a task to buy groceries"</li>
                  <li>"Show my tasks"</li>
                  <li>"Mark task 1 as completed"</li>
                  <li>"Update my meeting time"</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs sm:max-w-md md:max-w-lg lg:max-w-xl px-4 py-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : message.isError
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="whitespace-pre-wrap break-words">{message.content}</div>
                    {message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="mt-2 text-xs opacity-75">
                        <details className="mt-2">
                          <summary className="cursor-pointer hover:underline">Show tool calls</summary>
                          <div className="mt-2 space-y-2">
                            {message.tool_calls.map((call, idx) => (
                              <div key={idx} className="font-mono text-xs bg-black bg-opacity-5 p-2 rounded">
                                <div className="font-medium">{call.tool_name}:</div>
                                <pre className="mt-1 overflow-x-auto">
                                  {JSON.stringify(call.parameters, null, 2)}
                                </pre>
                                {call.result && (
                                  <div className="mt-1 pt-1 border-t border-gray-300">
                                    Result: {JSON.stringify(call.result)}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || !authToken}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !authToken}
            className="px-6 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}