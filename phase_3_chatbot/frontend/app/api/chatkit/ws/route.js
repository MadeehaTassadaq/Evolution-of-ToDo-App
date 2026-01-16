// This API route acts as a proxy to the backend ChatKit WebSocket endpoint
// However, Next.js doesn't directly support WebSocket connections in API routes
// So we'll return the backend URL for direct connection

import { NextResponse } from 'next/server';

export async function GET(request) {
  // Return the backend ChatKit WebSocket URL
  const backendWsUrl = `ws://localhost:8001/api/chatkit/ws`;

  return NextResponse.json({
    wsUrl: backendWsUrl,
    message: "ChatKit WebSocket proxy endpoint. Connect directly to the backend WebSocket."
  });
}

// For WebSocket connections, the client should connect directly to the backend
// since Next.js doesn't support WebSocket upgrades in edge runtime