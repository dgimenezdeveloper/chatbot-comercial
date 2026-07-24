import { auth } from "@/auth";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const { pathname } = req.nextUrl;

  const isProtectedRoute =
    pathname.startsWith("/dashboard") || pathname.startsWith("/onboarding");
  const isAuthRoute = pathname.startsWith("/login");

  if (isProtectedRoute && !isLoggedIn) {
    return Response.redirect(new URL("/login", req.nextUrl));
  }

  // Redirect already-authenticated users away from login
  if (isAuthRoute && isLoggedIn) {
    return Response.redirect(new URL("/dashboard", req.nextUrl));
  }
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
