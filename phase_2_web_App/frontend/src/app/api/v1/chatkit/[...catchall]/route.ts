/**
 * ChatKit API Proxy Route (Catch-all)
 * 
 * Handles all ChatKit sub-paths like /api/v1/chatkit/health, /api/v1/chatkit/threads, etc.
 * Proxies requests from browser to backend service.
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://backend-service:8000';

export async function GET(
  request: NextRequest, 
  { params }: { params: Promise<{ catchall?: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function POST(
  request: NextRequest, 
  { params }: { params: Promise<{ catchall?: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function PUT(
  request: NextRequest, 
  { params }: { params: Promise<{ catchall?: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function DELETE(
  request: NextRequest, 
  { params }: { params: Promise<{ catchall?: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function OPTIONS(
  request: NextRequest, 
  { params }: { params: Promise<{ catchall?: string[] }> }
) {
  return proxyRequest(request, await params);
}

async function proxyRequest(
  request: NextRequest, 
  resolvedParams: { catchall?: string[] }
): Promise<NextResponse> {
  try {
    const subPath = resolvedParams.catchall?.join('/') || '';
    
    // Build the target URL
    const targetUrl = new URL(`/api/v1/chatkit/${subPath}`, BACKEND_URL);
    
    // Preserve query parameters
    const searchParams = request.nextUrl.searchParams;
    for (const [key, value] of searchParams.entries()) {
      targetUrl.searchParams.set(key, value);
    }

    // Build fetch options with duplex for streaming
    const fetchOptions: RequestInit & { duplex?: string } = {
      method: request.method,
      headers: new Headers(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      duplex: 'half',
    };

    // Remove hop-by-hop headers
    const headers = fetchOptions.headers as Headers;
    headers.delete('host');
    headers.delete('content-length');
    headers.delete('transfer-encoding');
    headers.delete('connection');
    headers.set('host', new URL(BACKEND_URL).host);

    // Forward the request to the backend
    const backendResponse = await fetch(targetUrl.toString(), fetchOptions);

    // Create response with proper headers for SSE streaming
    const responseHeaders = new Headers(backendResponse.headers);
    responseHeaders.set('Cache-Control', 'no-cache');
    responseHeaders.set('Connection', 'keep-alive');
    responseHeaders.set('X-Accel-Buffering', 'no');
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    responseHeaders.set('Access-Control-Allow-Credentials', 'true');

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
