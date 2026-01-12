import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check for the token in cookies (first priority)
  const token = request.cookies.get('authToken')?.value

  // Allow access to login and register pages without token
  const pathname = request.nextUrl.pathname;
  if (pathname === '/login' || pathname === '/register') {
    // If already logged in and trying to access login, redirect to tasks
    if (token) {
      return NextResponse.redirect(new URL('/tasks', request.url));
    }
    return NextResponse.next();
  }

  // For protected routes, check if token exists
  if (!token) {
    // Redirect to login page for protected routes
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    // Specific protected routes
    '/tasks(.*)',
    '/dashboard(.*)',
  ],
}
