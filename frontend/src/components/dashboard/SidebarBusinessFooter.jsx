"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { getBusinessName, getBusinessLogo } from "@/lib/business-store";
import StoreIcon from "@/components/icons/dashboard/store";

/**
 * SidebarBusinessFooter — Client Component.
 *
 * Shows the business name and logo from localStorage.
 * Falls back to user name from session if no business data exists.
 * Does NOT use Google profile photo — the sidebar represents the business, not the user.
 *
 * Props:
 *   userName — user name from session (fallback for business name)
 */
export function SidebarBusinessFooter({ userName }) {
  const [businessName, setBusinessName] = useState(null);
  const [logoUrl, setLogoUrl] = useState(null);

  useEffect(() => {
    setBusinessName(getBusinessName(null));
    setLogoUrl(getBusinessLogo());
  }, []);

  const displayName = businessName || userName || "Mi Negocio";

  return (
    <div className="flex items-center gap-3 rounded-lg bg-background px-2 py-2">
      {/* Avatar: business logo if uploaded, otherwise StoreIcon */}
      {logoUrl ? (
        <Image
          src={logoUrl}
          alt={`Logo de ${displayName}`}
          width={36}
          height={36}
          className="size-9 shrink-0 rounded-full object-cover"
          unoptimized
        />
      ) : (
        <div className="flex size-9 shrink-0 items-center justify-center rounded-full border border-border bg-muted p-1.5">
          <StoreIcon className="size-full" />
        </div>
      )}

      {/* Labels */}
      <div className="min-w-0">
        <p className="text-xs text-muted-foreground">Tu negocio</p>
        <p className="truncate text-sm font-medium text-foreground">{displayName}</p>
      </div>
    </div>
  );
}
