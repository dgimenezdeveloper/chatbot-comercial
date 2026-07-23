"use client";

import { cva } from "class-variance-authority";
import {
  PieChart,
  Pie,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/ui/empty-state/empty-state";

const pieChartVariants = cva("w-full", {
  variants: {
    variant: {
      pie: "",
      donut: "",
    },
  },
  defaultVariants: { variant: "pie" },
});

const DEFAULT_COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#22c55e",
  "#eab308",
  "#ef4444",
  "#f97316",
  "#06b6d4",
  "#ec4899",
  "#14b8a6",
  "#f59e0b",
];

/**
 * Gráfico de torta/donut configurable con soporte para drill-down.
 *
 * @param {Object} props
 * @param {Array<{name: string, value: number, fill?: string}>} props.data - Datos del gráfico
 * @param {number} [props.innerRadius=0] - 0 = torta, >0 = donut
 * @param {Function} [props.onSliceClick] - Callback drill-down (FR-27)
 * @param {number} [props.height=300]
 * @param {boolean} [props.showTooltip=true]
 * @param {boolean} [props.showLegend=true]
 * @param {string} [props.className]
 */
export function MetricsPieChart({
  data,
  innerRadius = 0,
  onSliceClick,
  height = 300,
  showTooltip = true,
  showLegend = true,
  className,
}) {
  const coloredData = (data || []).map((entry, i) => ({
    ...entry,
    fill: entry.fill || DEFAULT_COLORS[i % DEFAULT_COLORS.length],
  }));

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-50">
        <EmptyState message="Sin datos disponibles" />
      </div>
    );
  }

  const variant = innerRadius > 0 ? "donut" : "pie";

  return (
    <div style={{ width: "100%", height: height || 300 }}>
      <ResponsiveContainer>
        <PieChart margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <Pie
            data={coloredData}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={"80%"}
            dataKey="value"
            nameKey="name"
            label={({ name, percent }) =>
              `${name} ${(percent * 100).toFixed(0)}%`
            }
            onClick={onSliceClick}
            style={onSliceClick ? { cursor: "pointer" } : undefined}
          />
          {showTooltip && <Tooltip />}
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: "16px", color: "#475569" }}
              formatter={(value) => (
                <span style={{ color: "#334155", fontSize: "13px" }}>
                  {value}
                </span>
              )}
            />
          )}
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export { pieChartVariants };