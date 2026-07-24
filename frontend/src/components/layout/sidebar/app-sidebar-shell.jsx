import LogoPymio from "@/components/icons/logo-pymio";
import { cn } from "@/lib/utils";

import { SidebarLogout } from "./sidebar-logout";

export function AppSidebarShell({ children, footer, className }) {
  return (
    <aside
      className={cn(
        "flex h-full w-sidebar shrink-0 flex-col",
        className,
      )}
    >
      {/* Logo area */}
      <div className="flex items-center justify-center px-6 py-6">
        <LogoPymio className="h-24 w-auto" aria-label="PYMIO" />
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-4 pb-4">
        {children}
      </div>

      <div className="space-y-3 border-t px-4 pt-6 pb-8">
        {footer}
        <SidebarLogout />
      </div>
    </aside>
  );
}
