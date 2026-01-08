const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface RegisterResponse {
  id?: string;
  email?: string;
  error?: string;
}

export interface LoginResponse {
  access_token?: string;
  token_type?: string;
  user_id?: string;
  error?: string;
}

export async function register(email: string, password: string): Promise<RegisterResponse> {
  try {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }), // Send password, backend will hash it
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      return { error: errorData.detail || `Registration failed: ${res.status}` };
    }

    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Registration error:', error);
    return { error: error instanceof Error ? error.message : 'Network error during registration' };
  }
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password); // Send the plain password, backend will hash it

    const res = await fetch(`${API_URL}/api/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      return { error: errorData.detail || `Login failed: ${res.status}` };
    }

    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Login error:', error);
    return { error: error instanceof Error ? error.message : 'Network error during login' };
  }
}
