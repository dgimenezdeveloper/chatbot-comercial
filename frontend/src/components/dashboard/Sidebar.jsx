"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { HelpCircle, Package } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { AgendaIcon } from "@/components/icons/AgendaIcon";
import { ClientesIcon } from "@/components/icons/ClientesIcon";
import { ConfiguracionIcon } from "@/components/icons/ConfiguracionIcon";
import { MetricasIcon } from "@/components/icons/MetricasIcon";
import { PanelIcon } from "@/components/icons/PanelIcon";
import { ServiciosIcon } from "@/components/icons/ServiciosIcon";
import { AppSidebarShell } from "@/components/layout/sidebar/app-sidebar-shell";
import { cn } from "@/lib/utils";
import { fetchNegocio } from "@/services/negocio-api";

export function Sidebar({ userFooter, onNavigate }) {
  const pathname = usePathname();

  const { data: business } = useQuery({
    queryKey: ["negocio"],
    queryFn: fetchNegocio,
    staleTime: 30 * 1000,
  });

  const enableServices = business?.enable_services ?? true;
  const enableProducts = business?.enable_products ?? true;
  const enableFaqs = business?.enable_faqs ?? true;

  const menuItems = [
    { label: "Panel",         href: "/dashboard",               icon: PanelIcon,        exact: true, show: true },
    { label: "Agenda",        href: "/dashboard/agenda",        icon: AgendaIcon,       show: true },
    { label: "Clientes",      href: "/dashboard/clientes",      icon: ClientesIcon,     show: true },
    { label: "Métricas",      href: "/dashboard/metrics",       icon: MetricasIcon,     show: true },
    { label: "Servicios",     href: "/dashboard/servicios",     icon: ServiciosIcon,    show: enableServices },
    { label: "Productos",     href: "/dashboard/productos",     icon: Package,          show: enableProducts },
    { label: "Preguntas Frecuentes", href: "/dashboard/faq",    icon: HelpCircle,       show: enableFaqs },
    { label: "Configuración", href: "/dashboard/configuracion", icon: ConfiguracionIcon, show: true },
  ];

  const visibleItems = menuItems.filter((item) => item.show);

  function isActiveRoute(currentPath, href, exact = false) {
    return exact ? currentPath === href : currentPath === href || currentPath.startsWith(`${href}/`);
  }

  return (
    <AppSidebarShell footer={userFooter}>
      <nav className="space-y-1">
        {visibleItems.map((item) => {
          const Icon = item.icon;
          const active = isActiveRoute(pathname, item.href, item.exact);

          return (
            <Link
              key={item.label}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-nav-active text-nav-active-foreground"
                  : "text-sidebar-foreground hover:bg-background hover:text-foreground",
              )}
            >
              <Icon className="size-5" />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </AppSidebarShell>
  );
}