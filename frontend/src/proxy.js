import { auth } from "@/auth";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const { pathname } = req.nextUrl;

  const isProtectedRoute =
    pathname.startsWith("/dashboard") || pathname.startsWith("/onboarding");
  const isAuthRoute = pathname.startsWith("/login");

  // 1. Si no está logueado y quiere entrar a rutas privadas -> Redirigir a /login
  if (isProtectedRoute && !isLoggedIn) {
    return Response.redirect(new URL("/login", req.nextUrl));
  }

  // 2. Si está logueado, evaluamos el estado de Onboarding
  if (isLoggedIn) {
    const user = req.auth?.user;

    // Regla SaaS:
    // - Inquilino 1 (Peluquería / Belén): Siempre completado (True).
    // - Inquilinos Nuevos (Barbería / ID >= 2): Depende del flag de PostgreSQL.
    const isCompleted = user?.business_id === 1 || user?.onboarding_completed === true;

    // Si intenta ir a /login estando logueado -> Mandar a su pantalla correspondiente
    if (isAuthRoute) {
      return Response.redirect(new URL(isCompleted ? "/dashboard" : "/onboarding", req.nextUrl));
    }

    // Si intenta ir a /dashboard sin haber hecho onboarding -> Mandar a /onboarding
    if (pathname.startsWith("/dashboard") && !isCompleted) {
      return Response.redirect(new URL("/onboarding", req.nextUrl));
    }

    // Si intenta ir a /onboarding habiéndolo completado -> Mandar a /dashboard
    if (pathname.startsWith("/onboarding") && isCompleted) {
      return Response.redirect(new URL("/dashboard", req.nextUrl));
    }
  }
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.jpeg$|.*\\.webp$|.*\\.svg$|.*\\.ico$).*)"],
};