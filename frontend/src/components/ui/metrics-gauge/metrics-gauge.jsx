"use client";

import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/ui/empty-state/empty-state";

// Colors resolved at runtime from CSS custom properties so they follow the theme.
// Fallback hex values are used only if CSS vars aren't available (e.g. SSR).
function getStatusColor(status) {
  if (typeof window === "undefined") {
    // SSR fallbacks — match the token values defined in globals.css
    return { ok: "hsl(142 71% 45%)", warning: "hsl(38 92% 50%)", critical: "hsl(0 84% 60%)" }[status] || "hsl(142 71% 45%)";
  }
  const style = getComputedStyle(document.documentElement);
  const map = {
    ok:       `hsl(${style.getPropertyValue("--success").trim()})`,
    warning:  `hsl(${style.getPropertyValue("--warning").trim()})`,
    critical: `hsl(${style.getPropertyValue("--destructive").trim()})`,
  };
  return map[status] || map.ok;
}

/**
 * Gauge semicircular implementado con SVG puro.
 * Confiable, sin dependencias de migración de Recharts v3.
 *
 * @param {{ value: number|null, status?: 'ok'|'warning'|'critical', label?: string, height?: number, className?: string }} props
 */
export function MetricsGauge({
  value,
  status = "ok",
  label,
  height = 200,
  className,
}) {
  if (value === null || value === undefined) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <EmptyState message="Sin datos" />
      </div>
    );
  }

  const clamped = Math.min(100, Math.max(0, value));
  const color = getStatusColor(status);

  
  const size = height * 0.8;
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius;
  const filledLength = (clamped / 100) * circumference;

  return (
    <div
      className={cn("relative flex flex-col items-center justify-center", className)}
      style={{ height }}
    >
      <svg
        width={size}
        height={size * 0.65}
        viewBox={`0 0 ${size} ${size * 0.65}`}
        style={{ overflow: "visible" }}
      >
       
        <path
          d={describeArc(size / 2, size * 0.6, radius, 180, 0)}
          fill="none"
          stroke="hsl(var(--border))"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        <path
          d={describeArc(size / 2, size * 0.6, radius, 180, 0)}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={`${filledLength} ${circumference}`}
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      </svg>

      
      <div className="absolute flex flex-col items-center justify-center" style={{ bottom: "8%" }}>
        <span className="text-2xl font-bold text-foreground" style={{ color }}>
          {clamped}%
        </span>
        {label && (
          <span className="mt-1 text-xs text-muted-foreground">
            {label}
          </span>
        )}
      </div>
    </div>
  );
}


function describeArc(cx, cy, radius, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, radius, endAngle);
  const end = polarToCartesian(cx, cy, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return [
    "M", start.x, start.y,
    "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
  ].join(" ");
}

function polarToCartesian(cx, cy, radius, angleInDegrees) {
  const angleInRadians = ((angleInDegrees - 180) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(angleInRadians),
    y: cy + (radius * Math.sin(angleInRadians)) * 0.55, 
  };
}