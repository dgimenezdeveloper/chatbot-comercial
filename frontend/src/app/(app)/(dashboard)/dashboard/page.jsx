import { auth } from "@/auth";
import { LayoutDashboard } from "lucide-react";

import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { AddAppointmentButton } from "@/components/features/agenda/AddAppointmentButton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table/table";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  confirmed: { label: "Confirmado", className: "bg-success/15 text-success border border-success/30" },
  confirmado: { label: "Confirmado", className: "bg-success/15 text-success border border-success/30" },
  completed: { label: "Completado", className: "bg-primary/15 text-primary border border-primary/30" },
  scheduled: { label: "Agendado", className: "bg-warning/15 text-warning-foreground border border-warning/40" },
  cancelled: { label: "Cancelado", className: "bg-destructive/10 text-destructive border border-destructive/30" },
  cancelado: { label: "Cancelado", className: "bg-destructive/10 text-destructive border border-destructive/30" },
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
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", config.className)}>
      {config.label}
    </span>
  );
}

export default async function DashboardPage() {
  const session = await auth();
  const token = session?.backendAccessToken;

  let stats = {
    todayAppointments: 0,
    depositsCobrados: 0,
    totalAppointments: 0,
    confirmedToday: 0,
  };

  let todayAppointments = [];
  let summary = { total: 0, confirmed: 0, pending: 0 };

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL
      ? `${process.env.NEXT_PUBLIC_API_URL}/calendar/turnos/`
      : "http://localhost:8000/api/v1/calendar/turnos/";

    const res = await fetch(apiUrl, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });

    if (res.ok) {
      const turnos = await res.json();
      const todayStr = new Date().toLocaleDateString("en-CA", { timeZone: "America/Argentina/Buenos_Aires" });

      const hoy = turnos.filter((t) => t.fecha === todayStr);

      stats.todayAppointments = hoy.length;
      stats.totalAppointments = turnos.length;
      stats.confirmedToday = hoy.filter((t) => t.estado === "confirmed" || t.estado === "confirmado" || t.estado === "completed").length;

      todayAppointments = hoy.map((t) => ({
        id: String(t.id),
        time: t.hora,
        client: t.nombre_cliente || (t.telefono ? `Cliente ${t.telefono.slice(-4)}` : "Cliente"),
        service: t.nombre_servicio || `Servicio #${t.servicio_id}`,
        status: t.estado,
      }));

      summary.total = turnos.length;
      summary.confirmed = turnos.filter((t) => t.estado === "confirmed" || t.estado === "confirmado" || t.estado === "completed").length;
      summary.pending = turnos.filter((t) => t.estado === "scheduled" || t.estado === "pendiente").length;
    }
  } catch (error) {
    console.error("Error al obtener panel de control:", error);
  }

  return (
    <DashboardPageLayout>
      <PageHeader
        icon={<LayoutDashboard className="size-5" />}
        title={`Panel de Control — ${session?.user?.name || "Administrador"}`}
      />

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard value={stats.todayAppointments} label="Turnos Hoy" />
        <StatCard value={`$${stats.depositsCobrados.toLocaleString("es-AR")}`} label="Señas cobradas" />
        <StatCard value={stats.totalAppointments} label="Turnos totales" />
        <StatCard value={stats.confirmedToday} label="Confirmados hoy" />
      </div>

      <section className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wide text-foreground">
            Turnos de Hoy
          </h2>
          <AddAppointmentButton />
        </div>

        <div className="overflow-hidden rounded-xl border border-border">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50 hover:bg-muted/50">
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">Hora</TableHead>
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">Cliente</TableHead>
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">Servicio</TableHead>
                <TableHead className="px-5 text-xs font-bold uppercase tracking-wide text-foreground">Estado</TableHead>
                <TableHead className="px-5 text-right text-xs font-bold uppercase tracking-wide text-foreground">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {todayAppointments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="px-5 py-8 text-center text-muted-foreground">
                    No hay turnos programados para hoy.
                  </TableCell>
                </TableRow>
              ) : (
                todayAppointments.map((appt) => (
                  <TableRow key={appt.id} className="border-border hover:bg-muted/30">
                    <TableCell className="px-5 py-4 font-medium text-foreground">{appt.time}</TableCell>
                    <TableCell className="px-5 py-4 text-foreground">{appt.client}</TableCell>
                    <TableCell className="px-5 py-4 text-muted-foreground">{appt.service}</TableCell>
                    <TableCell className="px-5 py-4">
                      <StatusBadge status={appt.status} />
                    </TableCell>
                    <TableCell className="px-5 py-4 text-right" />
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
            <span className="font-bold uppercase tracking-wide text-foreground">RESUMEN:</span>
            <span className="flex items-baseline gap-1.5">
              <span className="text-muted-foreground">Total:</span>
              <span className="font-bold text-foreground">{summary.total}</span>
            </span>
            <span className="flex items-baseline gap-1.5">
              <span className="text-muted-foreground">Confirmados:</span>
              <span className="font-bold text-foreground">{summary.confirmed}</span>
            </span>
            <span className="flex items-baseline gap-1.5">
              <span className="text-muted-foreground">Pendientes:</span>
              <span className="font-bold text-foreground">{summary.pending}</span>
            </span>
          </div>
        </div>
      </section>
    </DashboardPageLayout>
  );
}