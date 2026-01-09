import { getToken, clearAuth, isAuthenticated } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class AuthenticationError extends Error {
  constructor(message: string = 'Not authenticated') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

async function handle401(): Promise<void> {
  clearAuth();
  // Redirect to login page
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
  throw new AuthenticationError('Session expired. Please log in again.');
}

export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Don't make API call if no token is available for authenticated endpoints
  if (!isAuthenticated()) {
    throw new AuthenticationError('No authentication token found');
  }

  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    await handle401();
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `HTTP error ${response.status}`);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}