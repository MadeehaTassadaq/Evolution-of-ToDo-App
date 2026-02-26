import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Get the pathname
  const pathname = request.nextUrl.pathname;

  // Allow access to public assets, API routes, and static files without authentication
  if (
    pathname.startsWith('/api/') ||
    pathname.includes('/_next/') ||
    pathname.includes('/static/') ||
    pathname.includes('/public/') ||
    pathname.endsWith('.ico') ||
    pathname.endsWith('.png') ||
    pathname.endsWith('.jpg') ||
    pathname.endsWith('.jpeg') ||
    pathname.endsWith('.gif') ||
    pathname.endsWith('.svg') ||
    pathname.endsWith('.css') ||
    pathname.endsWith('.js') ||
    pathname.endsWith('.map') ||
    pathname.startsWith('/login') ||
    pathname.startsWith('/register')
  ) {
    return NextResponse.next();
  }

  // Check for the token in cookies for protected routes
  const token = request.cookies.get('authToken')?.value

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
     * - .well-known (security files)
     * - static (other static files)
     * - public (public assets)
     * - assets (asset files)
     */
    '/((?!api|_next/static|_next/image|_next/webpack-hmr|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
}
