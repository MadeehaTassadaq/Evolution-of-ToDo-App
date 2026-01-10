import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();

    // Forward the request to the backend
    const backendResponse = await fetch('http://localhost:8000/v1/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const backendData = await backendResponse.json();

    return NextResponse.json(backendData, {
      status: backendResponse.status,
    });
  } catch (error) {
    console.error('Error proxying register request:', error);
    return NextResponse.json(
      { error: 'Failed to process register request' },
      { status: 500 }
    );
  }
}