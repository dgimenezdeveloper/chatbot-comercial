import { MobileTopBar } from "@/components/layout/MobileTopBar";
import { Sidebar } from "@/components/dashboard/Sidebar";

/**
 * Server Component wrapper that composes MobileTopBar with the
 * dashboard Sidebar so DashboardLayout stays a Server Component.
 * Receives the pre-built userFooter from DashboardLayout.
 */
export function DashboardMobileBar({ userFooter }) {
  return <MobileTopBar sidebar={<Sidebar userFooter={userFooter} />} />;
}
