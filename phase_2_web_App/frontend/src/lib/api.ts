// Determine API base URL based on environment
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') return 'http://localhost:8000';

  const hostname = window.location.hostname;
  const port = window.location.port;

  // Running on Kubernetes NodePort (localhost:30080)
  // Backend is exposed on NodePort 30880
  if (port === '30080' || port === '30081') {
    return `${window.location.protocol}//${hostname}:30880`;
  }

  // Local development
  return 'http://localhost:8000';
};

const API_BASE = getApiBaseUrl();

export async function apiFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = typeof window !== "undefined"
    ? localStorage.getItem("authToken")
    : null;

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  // Global 401 handling
  if (response.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userId");
    window.location.href = "/login";
  }

  return response;
}
