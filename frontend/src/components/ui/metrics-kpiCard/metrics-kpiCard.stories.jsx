import { MetricsKpiCard } from "./metrics-kpiCard";

const meta = {
  component: MetricsKpiCard,
  title: "Components/Metrics/KpiCard",
};

export default meta;

export const Ok = {
  args: {
    title: "Conversión",
    value: "38%",
    status: "ok",
    trend: "up",
  },
};

export const Warning = {
  args: {
    title: "Autonomía",
    value: "45%",
    status: "warning",
    trend: "down",
  },
};

export const Critical = {
  args: {
    title: "No-Show",
    value: "22%",
    status: "critical",
  },
};

export const WithoutTrend = {
  args: {
    title: "CSAT",
    value: "4.2",
    status: "ok",
  },
};