"use client";

import { useState, Suspense } from "react";
import { signIn } from "next-auth/react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Lock, ArrowLeft, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card/card";

function LoginContent() {
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const searchParams = useSearchParams();
  const errorParam = searchParams.get("error");

  const handleGoogleSignIn = () => {
    setIsGoogleLoading(true);
    signIn("google", { redirectTo: "/dashboard" });
  };

  return (
    <Card className="w-full max-w-md shadow-lg">
      <CardHeader className="space-y-3 pb-4 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-accent bg-accent text-primary">
          <Lock className="h-6 w-6" />
        </div>

        <CardTitle className="text-2xl font-bold tracking-tight text-foreground">
          Acceso Restringido
        </CardTitle>

        <CardDescription className="text-sm leading-relaxed text-muted-foreground">
          Para ingresar al panel de control de tu comercio necesitas
          autenticarte. Inicia sesión con tu cuenta de Google autorizada.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4 pt-2">
        {/* Banner de error cuando el mail no está en la Lista Blanca */}
        {errorParam && (
          <div className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Acceso Denegado</p>
              <p className="mt-0.5">
                Tu cuenta de correo no se encuentra autorizada en la lista blanca de la plataforma. Contacta al administrador.
              </p>
            </div>
          </div>
        )}

        <Button
          variant="outline"
          onClick={handleGoogleSignIn}
          disabled={isGoogleLoading}
          className="flex h-12 w-full items-center justify-center gap-3 text-base font-medium shadow-sm"
        >
          {isGoogleLoading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              <span>Conectando con Google...</span>
            </>
          ) : (
            <>
              <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335" />
              </svg>
              <span>Continuar con Google</span>
            </>
          )}
        </Button>
      </CardContent>

      <CardFooter className="mt-2 flex flex-col items-center border-t border-border pt-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver a la página principal
        </Link>
      </CardFooter>
    </Card>
  );
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/50 p-4">
      <Suspense fallback={<div className="text-sm text-muted-foreground">Cargando...</div>}>
        <LoginContent />
      </Suspense>
    </div>
  );
}