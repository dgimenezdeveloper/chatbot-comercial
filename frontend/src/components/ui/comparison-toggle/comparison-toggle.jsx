"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button/button";
import { GitCompare } from "lucide-react";

/**
 * Toggle para activar/desactivar el modo comparación de períodos.
 *
 * @param {{ active: boolean, onToggle: () => void, comparisonDays: number, onDaysChange: (d: number) => void, className?: string }} props
 */
export function ComparisonToggle({
  active,
  onToggle,
  comparisonDays = 30,
  onDaysChange,
  className,
}) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Button
        variant={active ? "default" : "outline"}
        size="sm"
        onClick={onToggle}
      >
        <GitCompare className="h-4 w-4 mr-2" />
        {active ? "Comparando" : "Comparar períodos"}
      </Button>

      {active && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <span>vs</span>
          <div className="flex gap-1">
            {[7, 30, 90].map((p) => (
              <Button
                key={p}
                variant={comparisonDays === p ? "default" : "outline"}
                size="sm"
                onClick={() => onDaysChange(p)}
                className="text-xs"
              >
                {p}d
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}