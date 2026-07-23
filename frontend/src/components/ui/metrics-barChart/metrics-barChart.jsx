"use client";

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { EmptyState } from "@/components/ui/empty-state/empty-state";

const DEFAULT_FILL = "#6366f1";

/**
 * Gráfico de barras configurable con soporte para drill-down y comparativas.
 * Estilos 100% inline para evitar conflictos con Tailwind CSS.
 */
export function MetricsBarChart({
  data,
  bars = [],
  xKey = "name",
  layout = "vertical",
  comparisonData,
  onBarClick,
  height = 300,
  showTooltip = true,
  showLegend = true,
  className,
}) {
  const mergedData = useMemo(() => {
    if (!comparisonData || !comparisonData.length) return data || [];
    const cmpMap = new Map(comparisonData.map((d) => [d[xKey], d]));
    return (data || []).map((item) => {
      const cmp = cmpMap.get(item[xKey]);
      const merged = { ...item };
      if (cmp) {
        bars.forEach((bar) => {
          merged[`${bar.key}_prev`] = cmp[bar.key] ?? 0;
        });
      }
      return merged;
    });
  }, [data, comparisonData, xKey, bars]);

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-50">
        <EmptyState message="Sin datos disponibles" />
      </div>
    );
  }

  const isHorizontal = layout === "horizontal";

  return (
    <div className={className} style={{ width: "100%", height: height || 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={mergedData}
          layout={isHorizontal ? "horizontal" : "vertical"}
          margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          {isHorizontal ? (
            <>
              <YAxis
                type="category"
                dataKey={xKey}
                tick={{ fontSize: 12, fill: "#475569" }}
                width={120}
                axisLine={{ stroke: "#cbd5e1" }}
                tickLine={{ stroke: "#cbd5e1" }}
              />
              <XAxis
                type="number"
                tick={{ fontSize: 12, fill: "#475569" }}
                axisLine={{ stroke: "#cbd5e1" }}
                tickLine={{ stroke: "#cbd5e1" }}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey={xKey}
                tick={{ fontSize: 12, fill: "#475569" }}
                axisLine={{ stroke: "#cbd5e1" }}
                tickLine={{ stroke: "#cbd5e1" }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "#475569" }}
                axisLine={{ stroke: "#cbd5e1" }}
                tickLine={{ stroke: "#cbd5e1" }}
              />
            </>
          )}
          {showTooltip && (
            <Tooltip
              contentStyle={{
                background: "#fff",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
                fontSize: "13px",
                color: "#1e293b",
              }}
            />
          )}
          {showLegend && (
            <Legend
              wrapperStyle={{ fontSize: "13px", color: "#475569" }}
            />
          )}

          {bars.map((bar) => (
            <Bar
              key={bar.key}
              dataKey={bar.key}
              name={bar.label || bar.key}
              fill={bar.fill || DEFAULT_FILL}
              maxBarSize={30}
              radius={[0, 4, 4, 0]}
              onClick={onBarClick ? (d) => onBarClick(d) : undefined}
              cursor={onBarClick ? "pointer" : "default"}
            />
          ))}

          {comparisonData &&
            bars.map((bar) => (
              <Bar
                key={`${bar.key}-comparison`}
                dataKey={`${bar.key}_prev`}
                name={`${bar.label || bar.key} (anterior)`}
                fill={bar.fill || DEFAULT_FILL}
                maxBarSize={30}
                radius={[0, 4, 4, 0]}
                fillOpacity={0.3}
              />
            ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}