import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    const authHeader = request.headers.get('authorization');

    // Forward the request to the backend
    const backendResponse = await fetch('http://localhost:8000/v1/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || '',
      },
      body: JSON.stringify(body),
    });

    const backendData = await backendResponse.json();

    return NextResponse.json(backendData, {
      status: backendResponse.status,
    });
  } catch (error) {
    console.error('Error proxying chat request:', error);
    return NextResponse.json(
      { error: 'Failed to process chat request' },
      { status: 500 }
    );
  }
}