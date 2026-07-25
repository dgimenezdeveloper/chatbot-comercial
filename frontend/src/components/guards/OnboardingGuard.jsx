"use client";

/**
 * OnboardingGuard — Wrapper simplificado para compatibilidad.
 * 
 * La verificación de Onboarding y protección de rutas se realiza
 * de forma nativa en el servidor a través de Next.js Middleware (proxy.js).
 * Esto elimina la necesidad de usar hooks o SessionProvider en el cliente.
 */
export function OnboardingGuard({ children }) {
  return children;
}