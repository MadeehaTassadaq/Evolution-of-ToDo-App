// Utility functions for authentication token management

// Get token from either localStorage or cookies
export function getAuthToken(): string | null {
  // First check localStorage
  const tokenFromStorage = localStorage.getItem('authToken');
  if (tokenFromStorage) {
    return tokenFromStorage;
  }

  // Fallback to cookies
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('authToken='))
    ?.split('=')[1];

  return cookieValue || null;
}

// Store token in both localStorage and cookies
export function storeAuthToken(token: string, userId: string): void {
  // Store in localStorage for API calls
  localStorage.setItem('authToken', token);
  localStorage.setItem('userId', userId);

  // Store in cookies for middleware
  document.cookie = `authToken=${token}; path=/; max-age=86400; SameSite=Strict`;
  document.cookie = `userId=${userId}; path=/; max-age=86400; SameSite=Strict`;
}

// Clear all authentication tokens
export function clearAuthTokens(): void {
  // Clear cookies
  document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
  document.cookie = 'userId=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';

  // Clear localStorage
  localStorage.removeItem('authToken');
  localStorage.removeItem('userId');
}

// Check if user is authenticated
export function isAuthenticated(): boolean {
  return !!getAuthToken();
}

// Get user ID
export function getUserId(): string | null {
  const userIdFromStorage = localStorage.getItem('userId');
  if (userIdFromStorage) {
    return userIdFromStorage;
  }

  // Fallback to cookies
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('userId='))
    ?.split('=')[1];

  return cookieValue || null;
}