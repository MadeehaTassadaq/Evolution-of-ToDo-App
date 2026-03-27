/**
 * ChatKit API Proxy Route
 * 
 * Proxies all ChatKit widget requests from the browser to the backend service.
 * This allows the browser to use a relative URL (/api/v1/chatkit) instead of
 * needing to resolve internal Kubernetes DNS names.
 * 
 * Architecture:
 *   Browser → Frontend (/api/v1/chatkit) → Backend (http://backend-service:8000/api/v1/chatkit)
 */

import { NextRequest, NextResponse } from 'next/server';

// Backend service URL (internal Kubernetes DNS)
const BACKEND_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://backend-service:8000';

export async function GET(request: NextRequest) {
  return proxyRequest(request);
}

export async function POST(request: NextRequest) {
  return proxyRequest(request);
}

export async function PUT(request: NextRequest) {
  return proxyRequest(request);
}

export async function DELETE(request: NextRequest) {
  return proxyRequest(request);
}

async function proxyRequest(request: NextRequest): Promise<NextResponse> {
  try {
    // Build the target URL
    const targetUrl = new URL(request.url);
    targetUrl.protocol = 'http:';
    targetUrl.hostname = new URL(BACKEND_URL).hostname;
    targetUrl.port = new URL(BACKEND_URL).port || '8000';
    targetUrl.pathname = '/api/v1/chatkit';
    
    // Preserve query parameters (including auth token)
    const searchParams = request.nextUrl.searchParams;
    if (searchParams.has('token')) {
      targetUrl.searchParams.set('token', searchParams.get('token')!);
    }

    // Build fetch options with duplex for streaming
    const fetchOptions: RequestInit & { duplex?: string } = {
      method: request.method,
      headers: new Headers(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      duplex: 'half',
    };

    // Remove hop-by-hop headers that shouldn't be forwarded
    const headers = fetchOptions.headers as Headers;
    headers.delete('host');
    headers.delete('content-length');
    headers.delete('transfer-encoding');
    headers.delete('connection');
    
    // Set proper host header for backend
    headers.set('host', new URL(BACKEND_URL).host);

    // Forward the request to the backend
    const backendResponse = await fetch(targetUrl.toString(), fetchOptions);

    // Create response with proper headers for SSE streaming
    const responseHeaders = new Headers(backendResponse.headers);
    
    // Critical for SSE streaming - disable buffering
    responseHeaders.set('Cache-Control', 'no-cache');
    responseHeaders.set('Connection', 'keep-alive');
    responseHeaders.set('X-Accel-Buffering', 'no');
    
    // Handle CORS for browser access
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    responseHeaders.set('Access-Control-Allow-Credentials', 'true');

    // Return the proxied response with streaming support
    return new NextResponse(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });

  } catch (error) {
    console.error('[ChatKit Proxy] Error forwarding request:', error);
    return NextResponse.json(
      { 
        error: 'Failed to connect to ChatKit backend',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}

// Handle CORS preflight requests
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Allow-Credentials': 'true',
    },
  });
}
