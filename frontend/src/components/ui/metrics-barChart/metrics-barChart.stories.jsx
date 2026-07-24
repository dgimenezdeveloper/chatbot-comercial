import { MetricsBarChart } from "./metrics-barChart";

const meta = {
  component: MetricsBarChart,
  title: "Components/Metrics/BarChart",
};

export default meta;

const sampleData = [
  { name: "Lunes", count: 45 },
  { name: "Martes", count: 62 },
  { name: "Miércoles", count: 38 },
  { name: "Jueves", count: 71 },
  { name: "Viernes", count: 85 },
  { name: "Sábado", count: 22 },
];

const groupedData = [
  { name: "Lunes", bot: 30, manual: 15 },
  { name: "Martes", bot: 42, manual: 20 },
  { name: "Miércoles", bot: 28, manual: 10 },
  { name: "Jueves", bot: 51, manual: 20 },
  { name: "Viernes", bot: 60, manual: 25 },
];

export const Vertical = {
  args: {
    data: sampleData,
    bars: [{ key: "count", label: "Turnos", fill: "hsl(var(--primary))" }],
    xKey: "name",
    layout: "vertical",
    height: 300,
  },
};

export const Horizontal = {
  args: {
    data: sampleData,
    bars: [{ key: "count", label: "Turnos", fill: "hsl(var(--success))" }],
    xKey: "name",
    layout: "horizontal",
    height: 300,
  },
};

export const Grouped = {
  args: {
    data: groupedData,
    bars: [
      { key: "bot", label: "Bot", fill: "hsl(var(--primary))" },
      { key: "manual", label: "Manual", fill: "hsl(var(--muted-foreground))" },
    ],
    xKey: "name",
    layout: "vertical",
    height: 300,
  },
};

export const Empty = {
  args: {
    data: [],
    bars: [{ key: "count", label: "Turnos" }],
    xKey: "name",
    height: 300,
  },
};
