"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import {
  Sheet,
  SheetContent,
} from "@/components/ui/sheet/sheet";
import LogoPymio from "@/components/icons/logo-pymio";
import { cn } from "@/lib/utils";

/**
 * MobileTopBar — sticky top bar shown on mobile (< lg) for the dashboard.
 *
 * Hamburger opens a left-side Sheet with the sidebar content.
 * The Sheet's built-in close button (top-right X) is used — no custom X added.
 *
 * Props:
 *   sidebar   — the full sidebar React node to render inside the Sheet
 *   className — extra classes on the bar
 */
export function MobileTopBar({ sidebar, className }) {
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

      {/* Drawer — side=right, built-in X close button */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent
          side="right"
          className="w-[280px] p-0 bg-card border-l border-border"
        >
          <div className="h-full">
            {sidebar}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
