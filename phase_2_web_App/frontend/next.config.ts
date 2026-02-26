import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  // Allow external images if needed
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'localhost',
        port: '8001',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8001',
      },
      // Add patterns for deployed URLs
      {
        protocol: 'https',
        hostname: 'madeeha123-fastapi.hf.space',
      },
      {
        protocol: 'https',
        hostname: 'madeeha123-chatbot.hf.space',
      },
      // ChatKit CDN
      {
        protocol: 'https',
        hostname: 'chatkit.openai.com',
      },
    ],
  },
  // API rewrites for proxying to backend services
  async rewrites() {
    const chatbotApiUrl = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:7860';
    const todoApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    return [
      // Proxy ChatKit official endpoint to Phase 3 backend
      {
        source: '/api/v1/chatkit',
        destination: `${chatbotApiUrl}/api/v1/chatkit`,
      },
      // Proxy chat API requests to Phase 3 backend
      {
        source: '/api/chat/:path*',
        destination: `${chatbotApiUrl}/api/:path*`,
      },
      // Proxy todo API requests to Phase 2 backend
      {
        source: '/api/todo/:path*',
        destination: `${todoApiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
