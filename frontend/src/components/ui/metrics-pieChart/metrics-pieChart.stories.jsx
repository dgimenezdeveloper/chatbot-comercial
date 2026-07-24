import { MetricsPieChart } from "./metrics-pieChart";

const meta = {
  component: MetricsPieChart,
  title: "Components/Metrics/PieChart",
};

export default meta;

const pieData = [
  { name: "Completados", value: 65, fill: "#22c55e" },
  { name: "Cancelados", value: 20, fill: "#ef4444" },
  { name: "No-Show", value: 15, fill: "#eab308" },
];

export const Pie = {
  args: {
    data: pieData,
    height: 300,
  },
};

export const Donut = {
  args: {
    data: pieData,
    innerRadius: 60,
    height: 300,
  },
};

export const Empty = {
  args: {
    data: [],
  },
};