import { cn } from "@/lib/utils";

/**
 * AppShell — card-based layout wrapper shared by Dashboard and Onboarding.
 *
 * Desktop (≥ lg):
 *   bg-surface screen + p-6 padding → sidebar card + main card, gap-6 between them.
 *
 * Mobile (< lg):
 *   Sidebar is hidden. A `topBar` slot is rendered above the main card
 *   (e.g. MobileTopBar for dashboard, MobileStepIndicator for onboarding).
 *   The main card fills the full width without outer padding on mobile.
 *
 * Props:
 *   sidebar   — sidebar React node (hidden on mobile via CSS)
 *   topBar    — optional mobile-only header rendered above main content
 *   children  — main content area
 *   className — extra classes on the outer wrapper
 */
export default function AppShell({ sidebar, topBar, children, className }) {
  return (
    <div
      className={cn(
        "min-h-screen bg-surface",
        // Desktop: padding + flex row
        "lg:p-6 lg:flex lg:gap-6",
        className,
      )}
    >
      {/* Desktop sidebar card */}
      {sidebar && (
        <div
          className={cn(
            "hidden lg:flex",
            "shrink-0",
            "rounded-2xl bg-card shadow-sm",
            "sticky top-6 h-[calc(100vh-3rem)] overflow-hidden",
          )}
        >
          {sidebar}
        </div>
      )}

      {/* Main column (takes full width on mobile, flex-1 on desktop) */}
      <div className="flex flex-1 flex-col lg:rounded-2xl lg:bg-card lg:shadow-sm lg:min-h-[calc(100vh-3rem)]">
        {/* Content — on mobile bg-card fills naturally; desktop inherits the card */}
        <main className="flex-1 bg-card lg:bg-transparent lg:overflow-y-auto">
          {/* Mobile-only top slot rendered inside main so sticky works correctly.
              sticky positioning requires the element to share the same scroll
              container as the content that scrolls past it. */}
          {topBar && <div className="lg:hidden">{topBar}</div>}
          {children}
        </main>
      </div>
    </div>
  );
}
