import { cn } from "@/lib/utils";

/**
 * DashboardPageLayout — standard page wrapper for all dashboard pages.
 *
 * Ensures consistent padding and flex layout across every dashboard screen.
 * Wrap the entire page content (including PageHeader) in this component.
 *
 * Usage in any page:
 *   export default function MyPage() {
 *     return (
 *       <DashboardPageLayout>
 *         <PageHeader icon={...} title="..." />
 *         ...content...
 *       </DashboardPageLayout>
 *     );
 *   }
 */
export function DashboardPageLayout({ children, className }) {
  return (
    <div className={cn("flex flex-1 flex-col p-6 lg:p-8", className)}>
      {children}
    </div>
  );
}
