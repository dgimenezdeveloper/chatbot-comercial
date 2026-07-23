import { MetricsLineChart } from "./metrics-LineChart";

const meta = {
  component: MetricsLineChart,
  title: "UI/Metrics/LineChart",
};

export default meta;

const data = [
  { name: "Sem 1", valor: 32 },
  { name: "Sem 2", valor: 38 },
  { name: "Sem 3", valor: 29 },
  { name: "Sem 4", valor: 45 },
  { name: "Sem 5", valor: 41 },
  { name: "Sem 6", valor: 52 },
];

export const Simple = {
  args: {
    data,
    lines: [{ key: "valor", label: "Conversión %", stroke: "hsl(var(--primary))" }],
    xKey: "name",
    height: 300,
  },
};

export const Multiple = {
  args: {
    data,
    lines: [
      { key: "valor", label: "Conversión", stroke: "hsl(var(--primary))" },
      { key: "valor", label: "Objetivo", stroke: "#22c55e" },
    ],
    xKey: "name",
    height: 300,
  },
};

export const WithThreshold = {
  args: {
    data,
    lines: [{ key: "valor", label: "Conversión %", stroke: "hsl(var(--primary))" }],
    xKey: "name",
    threshold: { value: 30, label: "Alerta 30%", stroke: "hsl(var(--destructive))" },
    height: 300,
  },
};

export const WithArea = {
  args: {
    data,
    lines: [{ key: "valor", label: "Conversión %", stroke: "hsl(var(--primary))", area: true }],
    xKey: "name",
    height: 300,
  },
};

export const Empty = {
  args: {
    data: [],
    lines: [],
    xKey: "name",
  },
};