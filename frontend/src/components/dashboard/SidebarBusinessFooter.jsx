"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import StoreIcon from "@/components/icons/dashboard/store";
import { fetchNegocio } from "@/services/negocio-api";
import { getBusinessLogo } from "@/lib/business-store";

/**
 * SidebarBusinessFooter — Client Component.
 * Lee el nombre del negocio directamente desde PostgreSQL en Azure.
 */
export function SidebarBusinessFooter({ userName }) {
  const [businessName, setBusinessName] = useState(null);

  // Inicialización perezosa (Lazy initial state) para evitar setState síncrono en useEffect
  const [logoUrl] = useState(() => {
    if (typeof window === "undefined") return null;
    return getBusinessLogo();
  });

  useEffect(() => {
    let isMounted = true;

    async function loadName() {
      try {
        const data = await fetchNegocio();
        if (isMounted && data && data.nombre) {
          setBusinessName(data.nombre);
        }
      } catch (err) {
        console.error("Error al cargar nombre del negocio:", err);
      }
    }

    loadName();

    return () => {
      isMounted = false;
    };
  }, []);

  const displayName = businessName || userName || "Mi Negocio";

  return (
    <div className="flex items-center gap-3 rounded-lg bg-background px-2 py-2">
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

      <div className="min-w-0">
        <p className="text-xs text-muted-foreground">Tu negocio</p>
        <p className="truncate text-sm font-medium text-foreground">{displayName}</p>
      </div>
    </div>
  );
}