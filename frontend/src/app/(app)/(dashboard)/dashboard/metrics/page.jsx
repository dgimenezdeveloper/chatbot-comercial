import { MetricsDashboard } from "@/components/features/metrics/MetricsDashboard";

/**
 * Metrics page — renders the MetricsDashboard client component.
 *
 * Auth is handled automatically by the Axios interceptor (getSession),
 * so no need to pass accessToken as prop anymore.
 */
export default function MetricsPage() {
  return <MetricsDashboard />;
}
