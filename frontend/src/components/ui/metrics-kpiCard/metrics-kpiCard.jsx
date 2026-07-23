import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card/card";

const kpiCardVariants = cva(
  "flex flex-col items-center justify-center gap-2 rounded-xl border-2 p-6 transition-colors",
  {
    variants: {
      status: {
        ok: "border-emerald-200 bg-emerald-50/80 dark:border-emerald-800 dark:bg-emerald-950/60",
        warning:
          "border-amber-200 bg-amber-50/80 dark:border-amber-800 dark:bg-amber-950/60",
        critical: "border-rose-200 bg-rose-50/80 dark:border-rose-800 dark:bg-rose-950/60",
      },
    },
    defaultVariants: { status: "ok" },
  }
);

const trendIcon = {
  up: TrendingUp,
  down: TrendingDown,
  flat: Minus,
};

/**
 * Tarjeta numérica KPI con semáforo y tendencia opcional.
 * Colores suaves, alta legibilidad.
 *
 * @param {{ title: string, value: number|string, status?: 'ok'|'warning'|'critical', trend?: 'up'|'down'|'flat', className?: string }} props
 */
export function MetricsKpiCard({
  title,
  value,
  status = "ok",
  trend,
  className,
}) {
  const Icon = trend ? trendIcon[trend] : null;

  const valueColors = {
    ok: "text-emerald-700 dark:text-emerald-300",
    warning: "text-amber-700 dark:text-amber-300",
    critical: "text-rose-700 dark:text-rose-300",
  };

  const titleColors = {
    ok: "text-emerald-600/80 dark:text-emerald-400/80",
    warning: "text-amber-600/80 dark:text-amber-400/80",
    critical: "text-rose-600/80 dark:text-rose-400/80",
  };

  const trendColors = {
    up: "text-emerald-600 dark:text-emerald-400",
    down: "text-rose-600 dark:text-rose-400",
    flat: "text-amber-600 dark:text-amber-400",
  };

  return (
    <Card className={cn("border-0 shadow-sm hover:shadow-md transition-shadow", className)}>
      <CardContent className={cn(kpiCardVariants({ status }))}>
        <span className={cn("text-sm font-semibold", titleColors[status])}>
          {title}
        </span>
        <div className="flex items-center gap-2">
          <span className={cn("text-3xl font-bold", valueColors[status])}>
            {value}
          </span>
          {Icon && (
            <Icon className={cn("h-5 w-5", trendColors[trend])} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export { kpiCardVariants };