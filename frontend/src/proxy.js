import { auth } from "@/auth";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isDashboardRoute = req.nextUrl.pathname.startsWith("/dashboard");
  const isAuthRoute = req.nextUrl.pathname.startsWith("/login");

  if (isDashboardRoute && !isLoggedIn) {
    return Response.redirect(new URL("/login", req.nextUrl));
  }

  if (isAuthRoute && isLoggedIn) {
    return Response.redirect(new URL("/dashboard", req.nextUrl));
  }
});

// Ignore all requests that are not for the dashboard or login routes
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
