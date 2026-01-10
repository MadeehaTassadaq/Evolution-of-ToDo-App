import { NextResponse } from 'next/server';
import { headers } from 'next/headers';

export async function GET(request, { params }) {
  try {
    const headersList = headers();
    const authHeader = headersList.get('authorization');
    const url = new URL(request.url);
    const limit = url.searchParams.get('limit') || '50';
    const offset = url.searchParams.get('offset') || '0';

    // Forward the request to the backend
    const backendResponse = await fetch(
      `http://localhost:8000/v1/conversations/${params.conversation_id}/messages?limit=${limit}&offset=${offset}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader || '',
      },
    });

    const backendData = await backendResponse.json();

    return NextResponse.json(backendData, {
      status: backendResponse.status,
    });
  } catch (error) {
    console.error('Error proxying messages request:', error);
    return NextResponse.json(
      { error: 'Failed to fetch messages' },
      { status: 500 }
    );
  }
}