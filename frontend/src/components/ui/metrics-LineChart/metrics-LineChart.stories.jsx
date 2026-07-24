import { MetricsLineChart } from "./metrics-LineChart";

const meta = {
  component: MetricsLineChart,
  title: "Components/Metrics/LineChart",
};

export default meta;

const data = [
  { name: "Sem 1", conversion: 32, objetivo: 35 },
  { name: "Sem 2", conversion: 38, objetivo: 35 },
  { name: "Sem 3", conversion: 29, objetivo: 35 },
  { name: "Sem 4", conversion: 45, objetivo: 35 },
  { name: "Sem 5", conversion: 41, objetivo: 35 },
  { name: "Sem 6", conversion: 52, objetivo: 35 },
];

export const Simple = {
  args: {
    data,
    lines: [{ key: "conversion", label: "Conversión %", stroke: "hsl(var(--primary))" }],
    xKey: "name",
    height: 300,
  },
};

export const Multiple = {
  args: {
    data,
    lines: [
      { key: "conversion", label: "Conversión", stroke: "hsl(var(--primary))" },
      { key: "objetivo", label: "Objetivo", stroke: "hsl(var(--success))" },
    ],
    xKey: "name",
    height: 300,
  },
};

export const WithThreshold = {
  args: {
    data,
    lines: [{ key: "conversion", label: "Conversión %", stroke: "hsl(var(--primary))" }],
    xKey: "name",
    threshold: { value: 30, label: "Alerta 30%", stroke: "hsl(var(--destructive))" },
    height: 300,
  },
};

export const WithArea = {
  args: {
    data,
    lines: [{ key: "conversion", label: "Conversión %", stroke: "hsl(var(--primary))", area: true }],
    xKey: "name",
    height: 300,
  },
};

export const Empty = {
  args: {
    data: [],
    lines: [],
    xKey: "name",
    height: 300,
  },
};
