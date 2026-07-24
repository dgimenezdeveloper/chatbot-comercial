import { auth } from "@/auth";
import { MetricsDashboard } from "@/components/features/metrics/MetricsDashboard";

/**
 * Server Component — reads the session and passes the backend access token
 * to the MetricsDashboard Client Component.
 *
 * This avoids needing SessionProvider while keeping auth consistent
 * with the rest of the app (auth() server-side pattern).
 */
export default async function MetricsPage() {
  const session = await auth();
  const accessToken = session?.backendAccessToken ?? null;

  return <MetricsDashboard accessToken={accessToken} />;
}
