"use client";

import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Badge que indica que los datos mostrados están desactualizados.
 * Clickable para forzar un re-fetch.
 *
 * @param {{ isStale: boolean, onRefresh?: () => void, className?: string }} props
 */
export function StaleBadge({ isStale, onRefresh, className }) {
  if (!isStale) return null;

  return (
    <button
      type="button"
      onClick={onRefresh}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium",
        "bg-amber-100 text-amber-800 border border-amber-300",
        "dark:bg-amber-950 dark:text-amber-200 dark:border-amber-700",
        "hover:bg-amber-200 dark:hover:bg-amber-900 transition-colors",
        "cursor-pointer",
        className
      )}
      title="Click para actualizar los datos"
    >
      <AlertTriangle className="h-3.5 w-3.5" />
      Datos desactualizados
    </button>
  );
}