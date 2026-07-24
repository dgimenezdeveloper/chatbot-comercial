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
        "bg-[hsl(var(--cta)/0.15)] text-[hsl(var(--cta))] border border-[hsl(var(--cta)/0.4)]",
        "hover:bg-[hsl(var(--cta)/0.25)] transition-colors cursor-pointer",
        className
      )}
      title="Click para actualizar los datos"
    >
      <AlertTriangle className="h-3.5 w-3.5" />
      Datos desactualizados
    </button>
  );
}