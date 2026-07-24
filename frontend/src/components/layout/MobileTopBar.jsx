"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import { Sheet, SheetContent } from "@/components/ui/sheet/sheet";
import { Sidebar } from "@/components/dashboard/Sidebar";
import LogoPymio from "@/components/icons/logo-pymio";
import { cn } from "@/lib/utils";

/**
 * MobileTopBar — sticky top bar shown on mobile (< lg) for the dashboard.
 *
 * Builds its own Sidebar instance inside the Sheet and passes
 * onNavigate={() => setOpen(false)} so any nav link closes the drawer.
 *
 * Props:
 *   userFooter — pre-rendered Server Component node for the sidebar footer
 *   className  — extra classes on the bar
 */
export function MobileTopBar({ userFooter, className }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <header
        className={cn(
          "sticky top-0 z-40 flex items-center",
          "bg-card border-b border-border px-4 py-3",
          className,
        )}
      >
        {/* Spacer left — same width as hamburger button to keep logo centered */}
        <div className="w-9" aria-hidden="true" />

        {/* Brand logo — centered */}
        <div className="flex flex-1 justify-center">
          <LogoPymio className="h-8 w-[62px]" aria-label="PYMIO" />
        </div>

        {/* Hamburger — right side */}
        <button
          type="button"
          aria-label="Abrir menú"
          onClick={() => setOpen(true)}
          className="rounded-lg p-2 text-foreground transition-colors hover:bg-muted"
        >
          <Menu className="size-5" />
        </button>
      </header>

      {/* Drawer — side=right */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent
          side="right"
          className="w-[280px] p-0 bg-card border-l border-border"
        >
          <div className="h-full">
            <Sidebar
              userFooter={userFooter}
              onNavigate={() => setOpen(false)}
            />
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
