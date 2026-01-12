// We'll update this to use a cookie-based approach
// Since the AuthContext should handle token management, we'll create a helper function
function getCookieToken(): string | null {
  if (typeof document === 'undefined') {
    return null;
  }

  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.trim().startsWith('authToken='))
    ?.split('=')[1];

  return cookieValue || null;
}

// Function to clear auth state
export function clearAuth(): void {
  if (typeof document !== 'undefined') {
    // Clear cookies
    document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';
    document.cookie = 'userId=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';
  }

  if (typeof window !== 'undefined') {
    // Clear localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
  }
}

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
  // Try to get token from cookies first, fallback to localStorage
  let token = getCookieToken();
  if (!token && typeof window !== 'undefined') {
    token = localStorage.getItem('authToken');
  }

  // Don't make API call if no token is available for authenticated endpoints
  if (!token) {
    throw new AuthenticationError('No authentication token found');
  }

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