import { auth } from "@/auth";
import { Plus, LayoutDashboard } from "lucide-react";

import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table/table";
import {
  MOCK_STATS,
  MOCK_TODAY_APPOINTMENTS,
  MOCK_WEEKLY_SUMMARY,
} from "@/lib/data-mock/mock-dashboard";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  confirmed:       { label: "Confirmado",        className: "bg-success/15 text-success border border-success/30"              },
  pending_deposit: { label: "Pendiente de Seña", className: "bg-warning/15 text-warning-foreground border border-warning/40"   },
  expired:         { label: "Expirado",          className: "bg-destructive/10 text-destructive border border-destructive/30"  },
  unassigned:      { label: "Sin Asignar",       className: "bg-muted text-muted-foreground border border-border"              },
};

function StatCard({ value, label }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 rounded-xl border border-border bg-card px-6 py-5 text-center">
      <span className="text-3xl font-bold text-foreground">{value}</span>
      <span className="text-sm text-muted-foreground">{label}</span>
    </div>
  );
}

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? {
    label: status,
    className: "bg-muted text-muted-foreground border border-border",
  };
  return (
    <span className={cn(
      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
      config.className,
    )}>
      {config.label}
    </span>
  );
}

export default async function DashboardPage() {
  const session = await auth();
  const businessId = session?.user?.business_id ?? 1;

  // Si es Inquilino 1 (Peluquería), mostramos el dataset rico de prueba.
  // Si es Inquilino 2 (Barbería nuevo), se muestra vacía como corresponde a un nuevo cliente SaaS.
  const isTenantRico = businessId === 1;

  const stats = isTenantRico ? MOCK_STATS : {
    todayAppointments: 0,
    depositsCobrados: 0,
    botConsultas: 0,
    newClients: 0
  };

  const todayAppointments = isTenantRico ? MOCK_TODAY_APPOINTMENTS : [];
  
  const weeklySummary = isTenantRico ? MOCK_WEEKLY_SUMMARY : [
    { day: "Lunes", count: 0 },
    { day: "Martes", count: 0 },
    { day: "Miércoles", count: 0 },
    { day: "Jueves", count: 0 },
    { day: "Viernes", count: 0 },
    { day: "Sábado", count: 0 }
  ];

  return (
    <DashboardPageLayout>
      <PageHeader
        icon={<LayoutDashboard className="size-5" />}
        title={`Panel de Control — ${session?.user?.name || "Administrador"}`}
      />

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          value={stats.todayAppointments}
          label="Turnos Hoy"
        />
        <StatCard
          value={`$${stats.depositsCobrados.toLocaleString("es-AR")}`}
          label="Señas cobradas"
        />
        <StatCard
          value={stats.botConsultas}
          label="Consultas bot"
        />
        <StatCard
          value={stats.newClients}
          label="Clientes nuevos"
        />
      </div>

      <section className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wide text-foreground">
            Turnos de Hoy
          </h2>
          <Button variant="outline" size="sm">
            <Plus className="size-4" />
            Agregar turno manual
          </Button>
        </div>

        <div className="overflow-hidden rounded-xl border border-border">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50 hover:bg-muted/50">
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">
                  Hora
                </TableHead>
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">
                  Cliente
                </TableHead>
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">
                  Servicio
                </TableHead>
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">
                  Estado
                </TableHead>
                <TableHead className="px-5 text-right text-xs font-bold uppercase tracking-wide text-foreground">
                  Acciones
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {todayAppointments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="px-5 py-8 text-center text-muted-foreground">
                    No hay turnos agendados para hoy en este comercio.
                  </TableCell>
                </TableRow>
              ) : (
                todayAppointments.map((appt) => (
                  <TableRow key={appt.id} className="border-border hover:bg-muted/30">
                    <TableCell className="px-5 py-4 font-medium text-foreground">
                      {appt.time}
                    </TableCell>
                    <TableCell className="px-5 py-4 text-foreground">
                      {appt.client}
                    </TableCell>
                    <TableCell className="px-5 py-4 text-muted-foreground">
                      {appt.service}
                    </TableCell>
                    <TableCell className="px-5 py-4">
                      <StatusBadge status={appt.status} />
                    </TableCell>
                    <TableCell className="px-5 py-4 text-right">
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </section>

      <section>
        <div className="overflow-hidden rounded-xl border border-border">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-4 text-sm">
            <span className="font-bold uppercase tracking-wide text-foreground">
              Esta semana:
            </span>
            {weeklySummary.map((entry) => (
              <span key={entry.day} className="flex items-baseline gap-1.5">
                <span className="text-muted-foreground">{entry.day}</span>
                <span className="font-bold text-foreground">{entry.count}</span>
              </span>
            ))}
          </div>
        </div>
      </section>
    </DashboardPageLayout>
  );
}