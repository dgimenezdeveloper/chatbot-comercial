"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AgendaIcon } from "@/components/icons/AgendaIcon";
import { ClientesIcon } from "@/components/icons/ClientesIcon";
import { ConfiguracionIcon } from "@/components/icons/ConfiguracionIcon";
import { PanelIcon } from "@/components/icons/PanelIcon";
import { ServiciosIcon } from "@/components/icons/ServiciosIcon";
import { AppSidebarShell } from "@/components/layout/sidebar/app-sidebar-shell";
import { cn } from "@/lib/utils";

const menuItems = [
  { label: "Panel", href: "/dashboard", icon: PanelIcon, exact: true },
  { label: "Agenda", href: "/dashboard/agenda", icon: AgendaIcon },
  { label: "Clientes", href: "/dashboard/clientes", icon: ClientesIcon },
  { label: "Servicios", href: "/dashboard/servicios", icon: ServiciosIcon },
  {
    label: "Configuración",
    href: "/dashboard/configuracion",
    icon: ConfiguracionIcon,
  },
];

function isActiveRoute(pathname, href, exact = false) {
  if (exact) {
    return pathname === href;
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <AppSidebarShell
      footer={
        <div className="flex items-center gap-3 rounded-lg bg-background p-2">
          <div className="flex size-10 items-center justify-center rounded-lg bg-accent text-lg">
            🏪
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Tu negocio</p>
            <p className="text-sm font-medium text-foreground">Salón de Belleza</p>
          </div>
        </div>
      }
    >
      <nav className="space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActiveRoute(pathname, item.href, item.exact);

          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-nav-active text-nav-active-foreground"
                  : "text-sidebar-foreground hover:bg-background hover:text-foreground",
              )}
            >
              <Icon className="size-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </AppSidebarShell>
  );
}
