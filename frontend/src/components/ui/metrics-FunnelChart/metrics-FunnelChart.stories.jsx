import { MetricsFunnelChart } from "./metrics-FunnelChart";

const meta = {
  component: MetricsFunnelChart,
  title: "UI/Metrics/FunnelChart",
};

export default meta;

const fullFunnel = [
  { label: "Conversaciones iniciadas", value: 100, pct: 100 },
  { label: "Llegaron al menú principal", value: 78, pct: 78 },
  { label: 'Eligieron "sacar turno"', value: 61, pct: 61 },
  { label: "Completaron selección de servicio", value: 48, pct: 48 },
  { label: "Seleccionaron fecha y hora", value: 44, pct: 44 },
  { label: "Turno confirmado", value: 38, pct: 38 },
];

const shortFunnel = [
  { label: "Conversaciones iniciadas", value: 50, pct: 100 },
  { label: "Turno confirmado", value: 20, pct: 40 },
  { label: "Asistieron", value: 15, pct: 30 },
];

export const Full = {
  args: {
    steps: fullFunnel,
    height: 400,
  },
};

export const Short = {
  args: {
    steps: shortFunnel,
    height: 250,
  },
};

export const Empty = {
  args: {
    steps: [],
  },
};