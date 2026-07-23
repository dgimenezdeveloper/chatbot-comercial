"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from "recharts";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/ui/empty-state/empty-state";

/**
 * Gráfico de líneas configurable con soporte para umbral, área y comparativas.
 *
 * @param {Object} props
 * @param {Array} props.data - Datos del gráfico
 * @param {string} props.xKey - Clave para el eje X
 * @param {Array<{key: string, label?: string, stroke?: string, area?: boolean}>} props.lines - Definición de líneas
 * @param {{ value: number, label?: string, stroke?: string }} [props.threshold] - Línea de umbral
 * @param {Array<{key: string, label?: string, stroke?: string}>} [props.comparisonLines] - Líneas de comparación (FR-29)
 * @param {boolean} [props.showDots=true]
 * @param {boolean} [props.showTooltip=true]
 * @param {boolean} [props.showLegend=true]
 * @param {string} [props.className]
 */
export function MetricsLineChart({
  data,
  lines = [],
  xKey = "name",
  threshold,
  comparisonLines,
  showDots = true,
  showTooltip = true,
  showLegend = true,
  className,
}) {
  const mergedData = useMemo(() => {
    if (!comparisonLines || !comparisonLines.length) return data || [];
    const cmpMap = new Map(comparisonLines[0]?.data?.map?.((d) => [d[xKey], d]) || []);
    return (data || []).map((item) => {
      const merged = { ...item };
      comparisonLines.forEach((cl) => {
        const cmpData = cl.data || [];
        const match = cmpData.find((d) => d[xKey] === item[xKey]);
        if (match) {
          merged[`${cl.key}_prev`] = match[cl.key] ?? 0;
        }
      });
      return merged;
    });
  }, [data, comparisonLines, xKey]);

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-50">
        <EmptyState message="Sin datos disponibles" />
      </div>
    );
  }

  const DEFAULT_STROKE = "hsl(var(--primary))";
  const ChartType = lines.some((l) => l.area) ? ComposedChart : LineChart;

  return (
    <div className={cn("w-full h-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <ChartType
          data={mergedData}
          margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            className="stroke-muted dark:stroke-gray-700"
          />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 12 }}
            className="fill-foreground dark:fill-gray-300"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            className="fill-foreground dark:fill-gray-300"
          />
          {showTooltip && <Tooltip />}
          {showLegend && <Legend />}

          {threshold && (
            <ReferenceLine
              y={threshold.value}
              stroke={threshold.stroke || "hsl(var(--destructive))"}
              strokeDasharray="3 3"
              label={
                threshold.label
                  ? {
                      value: threshold.label,
                      position: "right",
                      className: "fill-destructive dark:fill-red-400 text-xs",
                    }
                  : undefined
              }
            />
          )}

          {lines.map((line) =>
            line.area ? (
              <Area
                key={line.key}
                type="monotone"
                dataKey={line.key}
                name={line.label || line.key}
                stroke={line.stroke || DEFAULT_STROKE}
                fill={line.stroke || DEFAULT_STROKE}
                fillOpacity={0.15}
                dot={showDots}
              />
            ) : (
              <Line
                key={line.key}
                type="monotone"
                dataKey={line.key}
                name={line.label || line.key}
                stroke={line.stroke || DEFAULT_STROKE}
                dot={showDots}
              />
            )
          )}

          {comparisonLines?.map((line) => (
            <Line
              key={`${line.key}-comparison`}
              type="monotone"
              dataKey={`${line.key}_prev`}
              name={`${line.label || line.key} (anterior)`}
              stroke={line.stroke || DEFAULT_STROKE}
              strokeDasharray="5 5"
              dot={false}
            />
          ))}
        </ChartType>
      </ResponsiveContainer>
    </div>
  );
}