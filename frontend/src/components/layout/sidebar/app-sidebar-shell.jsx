import LogoPymio from "@/components/icons/logo-pymio";
import { cn } from "@/lib/utils";

import { SidebarLogout } from "./sidebar-logout";

export function AppSidebarShell({ children, footer, className }) {
  return (
    <aside
      className={cn(
        "flex h-screen w-sidebar shrink-0 flex-col border-r bg-sidebar",
        className,
      )}
    >
      <div className="px-10 py-10">
        <div className="flex h-24 w-full items-center justify-center">
          <LogoPymio className="h-full w-full" aria-label="PYMIO" />
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-10 py-10">
        {children}
      </div>

      <div className="space-y-3 border-t p-4">
        {footer}
        <SidebarLogout />
      </div>
    </aside>
  );
}
