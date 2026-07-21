import { PanelIcon } from "@/components/icons/PanelIcon";
import { AgendaIcon } from "@/components/icons/AgendaIcon";
import { ClientesIcon } from "@/components/icons/ClientesIcon";
import { ServiciosIcon } from "@/components/icons/ServiciosIcon";
import { ConfiguracionIcon } from "@/components/icons/ConfiguracionIcon";

const menuItems = [
  { label: "Panel", href: "/dashboard", icon: PanelIcon },
  { label: "Agenda", href: "/dashboard/agenda", icon: AgendaIcon },
  { label: "Clientes", href: "/dashboard/clientes", icon: ClientesIcon },
  { label: "Servicios", href: "/dashboard/servicios", icon: ServiciosIcon },
  { label: "Configuración", href: "/dashboard/configuracion", icon: ConfiguracionIcon },
];

export function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-white border-r border-gray-200 flex flex-col">
      {/* Logo / nombre del negocio */}
      <div className="p-6 border-b border-gray-200">
        <span className="text-xl font-bold text-gray-800">HairBot</span>
      </div>

      {/* Menú de navegación */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            
             <a key={item.label}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>

            </a>
          );
        })}
      </nav>

      {/* Bloque inferior */}
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-400">Tu negocio</p>
        <p className="text-sm font-medium text-gray-700">Salón de Belleza</p>
      </div>
    </aside>
  );
}