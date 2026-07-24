import { MobileTopBar } from "@/components/layout/MobileTopBar";

/**
 * Server Component wrapper — passes userFooter to MobileTopBar.
 * MobileTopBar builds its own Sidebar instance client-side so it can
 * wire onNavigate={() => setOpen(false)} without prop-drilling through
 * a pre-rendered Server Component node.
 */
export function DashboardMobileBar({ userFooter }) {
  return <MobileTopBar userFooter={userFooter} />;
}
