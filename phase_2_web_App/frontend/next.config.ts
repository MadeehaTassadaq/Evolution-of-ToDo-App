import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
    ],
  },
  // Disable Turbopack for compatibility if needed
  experimental: {
    // Remove problematic rewrites that may interfere with asset loading
  },
};

export default nextConfig;
