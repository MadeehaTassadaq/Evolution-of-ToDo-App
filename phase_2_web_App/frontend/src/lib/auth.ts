// SSR-safe auth utilities - Updated to prioritize cookies
function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

export function getToken(): string | null {
  if (typeof document === 'undefined') {
    return null;
  }

  // Prioritize cookies over localStorage for consistency
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.trim().startsWith('authToken='))
    ?.split('=')[1];

  if (cookieValue) {
    // Ensure token is also in localStorage for API calls
    if (isBrowser()) {
      localStorage.setItem('authToken', cookieValue);
    }
    return cookieValue;
  }

  // Fallback to localStorage if cookies are not available
  if (isBrowser()) {
    return localStorage.getItem('authToken');
  }

  return null;
}

export function isAuthenticated(): boolean {
  const token = getToken();
  return token !== null && token.length > 0;
}

export function clearAuth(): void {
  if (typeof document !== 'undefined') {
    // Clear cookies
    document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';
    document.cookie = 'userId=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; Secure';
  }

  if (isBrowser()) {
    // Clear localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
  }
}