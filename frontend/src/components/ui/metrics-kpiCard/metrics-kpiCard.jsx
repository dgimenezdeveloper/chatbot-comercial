import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card/card";

/**
 * KPI card with traffic-light status and optional trend icon.
 * Uses semantic status tokens: success / warning / destructive.
 */
const kpiCardVariants = cva(
  "flex flex-col items-center justify-center gap-2 rounded-xl border-2 p-6 transition-colors",
  {
    variants: {
      status: {
        ok:       "border-success/30 bg-success/10 text-success-foreground",
        warning:  "border-warning/40 bg-warning/15 text-warning-foreground",
        critical: "border-destructive/40 bg-destructive/10 text-destructive",
      },
    },
    defaultVariants: { status: "ok" },
  }
);

const trendIcon = {
  up:   TrendingUp,
  down: TrendingDown,
  flat: Minus,
};

const valueColorMap = {
  ok:       "text-success",
  warning:  "text-warning-foreground",
  critical: "text-destructive",
};

const titleColorMap = {
  ok:       "text-success/80",
  warning:  "text-warning-foreground/80",
  critical: "text-destructive/80",
};

const trendColorMap = {
  up:   "text-success",
  down: "text-destructive",
  flat: "text-muted-foreground",
};

export function MetricsKpiCard({ title, value, status = "ok", trend, className }) {
  const Icon = trend ? trendIcon[trend] : null;

  return (
    <Card className={cn("border-0 shadow-sm transition-shadow hover:shadow-md py-0", className)}>
      <CardContent className={cn(kpiCardVariants({ status }))}>
        <span className={cn("text-sm font-semibold", titleColorMap[status])}>
          {title}
        </span>
        <div className="flex items-center gap-2">
          <span className={cn("text-3xl font-bold", valueColorMap[status])}>
            {value}
          </span>
          {Icon && (
            <Icon className={cn("size-5", trendColorMap[trend])} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export { kpiCardVariants };
