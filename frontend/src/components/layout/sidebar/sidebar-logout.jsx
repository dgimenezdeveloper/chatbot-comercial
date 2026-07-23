"use client";

import { LogOut } from "lucide-react";
import { signOut } from "next-auth/react";

import { cn } from "@/lib/utils";

export function SidebarLogout({ className }) {
  return (
    <button
      type="button"
      onClick={() => signOut({ redirectTo: "/" })}
      className={cn(
        "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-background hover:text-foreground",
        className,
      )}
    >
      <LogOut className="size-5" />
      <span>Cerrar sesión</span>
    </button>
  );
}
