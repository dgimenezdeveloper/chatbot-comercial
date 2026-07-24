import { AlertCircle, RefreshCw, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button/button";

/**
 * ErrorState — reusable error display for when API calls fail.
 *
 * Shows contextual icon, title, description, technical detail (collapsible),
 * and a retry button.
 *
 * Props:
 *   title    — custom title (auto-detected from error if not provided)
 *   message  — the error message string
 *   onRetry  — callback for retry button (optional, hides button if not provided)
 */
export function ErrorState({ title, message = "Error desconocido", onRetry }) {
  const isAuthError = message?.includes("401") || message?.includes("autenticado");
  const isNetworkError = message?.includes("conexión") || message?.includes("Network") || message?.includes("ECONNREFUSED");

  const displayTitle = title || (
    isAuthError
      ? "Sesión expirada"
      : isNetworkError
        ? "Sin conexión al servidor"
        : "Error al cargar datos"
  );

  const displayDescription = isAuthError
    ? "Tu sesión expiró o no tenés permisos. Intentá cerrar sesión y volver a ingresar."
    : isNetworkError
      ? "No se pudo conectar con el servidor. Verificá que el backend esté corriendo."
      : "Ocurrió un error inesperado. Podés volver a intentar.";

  const Icon = isNetworkError ? WifiOff : AlertCircle;

  return (
    <div className="flex flex-col items-center gap-4 py-12 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-destructive/10">
        <Icon className="size-6 text-destructive" />
      </div>

      <div className="max-w-sm space-y-1">
        <h3 className="text-base font-semibold text-foreground">{displayTitle}</h3>
        <p className="text-sm text-muted-foreground">{displayDescription}</p>
      </div>

      <details className="w-full max-w-sm rounded-lg border border-border bg-muted/50 px-4 py-2 text-left">
        <summary className="cursor-pointer text-xs font-medium text-muted-foreground">
          Detalle técnico
        </summary>
        <p className="mt-2 break-all font-mono text-xs text-destructive">
          {message}
        </p>
      </details>

      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="mt-2">
          <RefreshCw className="size-4" />
          Reintentar
        </Button>
      )}
    </div>
  );
}
