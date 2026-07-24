import Image from "next/image";
import Link from "next/link";
import { Home } from "lucide-react";

/**
 * 404 page for app routes (dashboard, onboarding, auth).
 *
 * This is activated when a Server Component calls notFound() explicitly
 * within the (app) route group. For example, when fetching a resource
 * by ID that doesn't exist.
 *
 * For routes that simply don't match any segment, Next.js uses the
 * root not-found.js instead.
 */
export default function AppNotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 py-12">
      {/* Main content */}
      <div className="mx-auto flex w-full max-w-4xl flex-col items-center gap-8 lg:flex-row lg:items-center lg:gap-12">

        {/* Left — text */}
        <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
          <h1 className="font-title text-7xl font-bold text-primary sm:text-8xl">
            404
          </h1>

          <h2 className="mt-3 font-title text-xl font-bold text-foreground sm:text-2xl">
            Ups... esta pagina se tomo un descanso
          </h2>

          <p className="mt-3 max-w-sm text-sm text-muted-foreground">
            Parece que el lugar que buscas no existe o se fue de vacaciones 🌴
          </p>

          {/* CTA */}
          <Link
            href="/dashboard"
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
          >
            <Home className="size-4" />
            Volver al panel
          </Link>
        </div>

        {/* Right — illustration */}
        <div className="flex items-center justify-center">
          <Image
            src="/404-dashboard.png"
            alt="Robot Pymio confundido"
            width={450}
            height={400}
            className="h-auto w-full max-w-xs sm:max-w-sm lg:max-w-md"
            priority
          />
        </div>
      </div>

      {/* Bottom banner */}
      <div className="mt-10 w-full max-w-xl rounded-xl border border-border bg-muted/50 px-6 py-4 text-center">
        <p className="text-sm text-muted-foreground">
          <span className="mr-1">💡</span>
          Mientras tanto, Pymio estara atendiendo a tus clientes por vos
          <span className="ml-1">😉</span>
        </p>
      </div>

      {/* Secondary CTA below banner */}
      <Link
        href="/dashboard"
        className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
      >
        <Home className="size-3.5" />
        Ir al panel de control
      </Link>
    </div>
  );
}
