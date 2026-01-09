import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check for the token in cookies (first priority)
  let token = request.cookies.get('authToken')?.value

  // If not in cookies, we could also check for other methods, but typically
  // for Next.js middleware, cookies are the most reliable way to check auth
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/tasks(.*)', '/dashboard(.*)'], // Updated to match more protected routes if needed
}
