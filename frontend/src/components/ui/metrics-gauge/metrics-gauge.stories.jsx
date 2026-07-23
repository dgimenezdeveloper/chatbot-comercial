import { MetricsGauge } from "./metrics-gauge";

const meta = {
  component: MetricsGauge,
  title: "UI/Metrics/Gauge",
};

export default meta;

export const Ok = {
  args: {
    value: 75,
    status: "ok",
    label: "Resolución Autónoma",
    height: 200,
  },
};

export const Warning = {
  args: {
    value: 45,
    status: "warning",
    label: "Tasa Fallback",
    height: 200,
  },
};

export const Critical = {
  args: {
    value: 12,
    status: "critical",
    label: "Conversión",
    height: 200,
  },
};

export const Empty = {
  args: {
    value: null,
    label: "Sin datos",
  },
};