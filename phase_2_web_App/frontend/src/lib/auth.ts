// SSR-safe auth utilities
function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

export function getToken(): string | null {
  if (!isBrowser()) {
    return null;
  }
  return localStorage.getItem('token');
}

export function isAuthenticated(): boolean {
  const token = getToken();
  return token !== null && token.length > 0;
}

export function clearAuth(): void {
  if (!isBrowser()) {
    return;
  }
  localStorage.removeItem('token');
}