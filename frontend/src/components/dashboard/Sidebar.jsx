"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AgendaIcon } from "@/components/icons/AgendaIcon";
import { ClientesIcon } from "@/components/icons/ClientesIcon";
import { ConfiguracionIcon } from "@/components/icons/ConfiguracionIcon";
import { MetricasIcon } from "@/components/icons/MetricasIcon";
import { PanelIcon } from "@/components/icons/PanelIcon";
import { ServiciosIcon } from "@/components/icons/ServiciosIcon";
import { AppSidebarShell } from "@/components/layout/sidebar/app-sidebar-shell";
import { cn } from "@/lib/utils";

const menuItems = [
  { label: "Panel",         href: "/dashboard",               icon: PanelIcon,        exact: true },
  { label: "Agenda",        href: "/dashboard/agenda",        icon: AgendaIcon        },
  { label: "Clientes",      href: "/dashboard/clientes",      icon: ClientesIcon      },
  { label: "Métricas",      href: "/dashboard/metrics",       icon: MetricasIcon      },
  { label: "Servicios",     href: "/dashboard/servicios",     icon: ServiciosIcon     },
  { label: "Configuración", href: "/dashboard/configuracion", icon: ConfiguracionIcon },
];

function isActiveRoute(pathname, href, exact = false) {
  return exact ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);
}

/**
 * Sidebar receives the pre-rendered `userFooter` as a prop so this Client
 * Component doesn't need to call `auth()` directly (which requires a Server
 * Component context). The footer is built in DashboardLayout as a Server
 * Component and passed down.
 */
export function Sidebar({ userFooter }) {
  const pathname = usePathname();

  return (
    <AppSidebarShell footer={userFooter}>
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
