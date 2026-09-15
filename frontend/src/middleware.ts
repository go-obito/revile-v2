import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const refreshToken = request.cookies.get("refresh_token")?.value;
  if (!refreshToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
