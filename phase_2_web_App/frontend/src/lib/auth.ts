// SSR-safe auth utilities
function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

export function getToken(): string | null {
  if (!isBrowser()) {
    return null;
  }
  // Check both localStorage and cookies for token consistency
  let token = localStorage.getItem('authToken');
  if (!token) {
    // Try to get from cookies as fallback
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('authToken='))
      ?.split('=')[1];
    if (cookieValue) {
      token = cookieValue;
      // Store in localStorage for API calls
      localStorage.setItem('authToken', cookieValue);
    }
  }
  return token;
}

export function isAuthenticated(): boolean {
  const token = getToken();
  return token !== null && token.length > 0;
}

export function clearAuth(): void {
  if (!isBrowser()) {
    return;
  }
  // Clear both localStorage and cookies for consistency
  document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
  document.cookie = 'userId=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';

  localStorage.removeItem('authToken');
  localStorage.removeItem('userId');
}