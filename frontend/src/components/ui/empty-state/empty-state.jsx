import { BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Placeholder para estados vacíos en componentes de gráficos.
 *
 * @param {{ message?: string, icon?: React.ElementType, className?: string }} props
 */
export function EmptyState({
  message = "Sin datos disponibles",
  icon: Icon = BarChart3,
  className,
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 h-full min-h-0 text-muted-foreground",
        className
      )}
    >
      <Icon className="h-12 w-12 opacity-40" />
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}