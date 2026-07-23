"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/ui/empty-state/empty-state";

/**
 * Custom Tooltip para el funnel de conversión.
 */
function FunnelTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;
  return (
    <div className="rounded-lg border bg-white dark:bg-gray-800 dark:border-gray-700 p-3 shadow-md text-sm">
      <p className="font-semibold text-foreground dark:text-gray-100">{data.label}</p>
      <p className="text-muted-foreground dark:text-gray-300">
        Usuarios: <strong>{data.value}</strong>
      </p>
      {data.dropPct != null && (
        <p className="text-red-500 dark:text-red-400">
          -{data.dropPct}% vs paso anterior
        </p>
      )}
      <p className="text-muted-foreground dark:text-gray-400 text-xs">
        {data.totalPct}% del inicio
      </p>
    </div>
  );
}

/**
 * Funnel de conversión implementado con BarChart.
 * Muestra barras decrecientes con % de caída entre pasos.
 *
 * @param {{ steps: Array<{label: string, value: number, pct: number}>, onStepClick?: Function, height?: number, className?: string }} props
 */
export function MetricsFunnelChart({
  steps = [],
  onStepClick,
  height = 350,
  className,
}) {
  if (!steps || steps.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <EmptyState message="Sin datos disponibles" />
      </div>
    );
  }

  // Construir datos con campos calculados para tooltip
  const initialValue = steps[0]?.value || 1;
  const data = steps.map((step, i) => {
    const prevValue = i > 0 ? steps[i - 1].value : step.value;
    const dropPct =
      i > 0 && prevValue > 0
        ? Math.round(((prevValue - step.value) / prevValue) * 100)
        : null;
    return {
      ...step,
      label: step.label,
      dropPct: i === 0 ? null : dropPct,
      totalPct: Math.round((step.value / initialValue) * 100),
    };
  });

  // Colores secuenciales (oscureciendo progresivamente)
  const colors = [
    "hsl(var(--primary))",
    "hsl(var(--primary) / 0.8)",
    "hsl(var(--primary) / 0.65)",
    "hsl(var(--primary) / 0.5)",
    "hsl(var(--primary) / 0.35)",
    "hsl(var(--primary) / 0.2)",
  ];

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          barCategoryGap="15%"
        >
          <CartesianGrid
            strokeDasharray="3 3"
            horizontal={false}
            className="stroke-muted dark:stroke-gray-700"
          />
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fontSize: 13 }}
            className="fill-foreground dark:fill-gray-300"
            width={140}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<FunnelTooltip />} />
          <Bar
            dataKey="value"
            radius={[0, 6, 6, 0]}
            onClick={onStepClick ? (d) => onStepClick(d) : undefined}
            style={onStepClick ? { cursor: "pointer" } : undefined}
            fill={colors[0]}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Anotaciones */}
      <div className="flex flex-wrap gap-4 justify-center mt-2">
        {data.slice(1).map((step, i) => (
          <span
            key={`drop-${i}`}
            className="text-xs text-red-500 dark:text-red-400 font-medium"
          >
            {step.label.split(" (")[0]}: -{step.dropPct}%
          </span>
        ))}
      </div>
    </div>
  );
}