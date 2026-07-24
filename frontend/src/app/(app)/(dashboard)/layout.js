import { Sidebar } from "@/components/dashboard/Sidebar";
import { SidebarUserFooter } from "@/components/dashboard/SidebarUserFooter";
import { DashboardMobileBar } from "@/components/dashboard/DashboardMobileBar";
import AppShell from "@/components/layout/AppShell";

export default async function DashboardLayout({ children }) {
  // Build the user footer once here (Server Component) and pass it down
  // to the client Sidebar via props — avoids calling auth() in a Client Component.
  const userFooter = <SidebarUserFooter />;

  return (
    <AppShell
      sidebar={<Sidebar userFooter={userFooter} />}
      topBar={<DashboardMobileBar userFooter={userFooter} />}
    >
      {children}
    </AppShell>
  );
}
