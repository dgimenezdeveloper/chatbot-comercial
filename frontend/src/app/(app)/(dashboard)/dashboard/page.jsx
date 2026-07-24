import { Plus, LayoutDashboard } from "lucide-react";

import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/badge/badge";
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
} from "@/lib/data/mock-dashboard";
import { cn } from "@/lib/utils";

// ─── Status config ────────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  confirmed:       { label: "Confirmado",        variant: "secondary"    },
  pending_deposit: { label: "Pendiente de Seña", variant: "outline"      },
  expired:         { label: "Expirado",           variant: "destructive"  },
  unassigned:      { label: "Sin Asignar",        variant: "outline"      },
};

// ─── Sub-components ───────────────────────────────────────────────────────────

/**
 * StatCard — one of the four metric cards at the top.
 */
function StatCard({ value, label }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 rounded-xl border border-border bg-card px-6 py-5 text-center">
      <span className="text-3xl font-bold text-foreground">{value}</span>
      <span className="text-sm text-muted-foreground">{label}</span>
    </div>
  );
}

/**
 * StatusBadge — renders the appointment status pill.
 */
function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? { label: status, variant: "outline" };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  // Format today's date in Spanish
  const today = new Date().toLocaleDateString("es-AR", {
    weekday: "long",
    day:     "numeric",
    month:   "long",
    year:    "numeric",
  });
  // Capitalize first letter
  const todayLabel = today.charAt(0).toUpperCase() + today.slice(1);

  return (
    <DashboardPageLayout>
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <PageHeader
        icon={<LayoutDashboard className="size-5" />}
        title="Panel de Control — Administrador"
        subtitle={todayLabel}
      />

      {/* ── Stats row ─────────────────────────────────────────────────────── */}
      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          value={MOCK_STATS.todayAppointments}
          label="Turnos Hoy"
        />
        <StatCard
          value={`$${MOCK_STATS.depositsCobrados.toLocaleString("es-AR")}`}
          label="Señas cobradas"
        />
        <StatCard
          value={MOCK_STATS.botConsultas}
          label="Consultas bot"
        />
        <StatCard
          value={MOCK_STATS.newClients}
          label="Clientes nuevos"
        />
      </div>

      {/* ── Today's appointments ──────────────────────────────────────────── */}
      <section className="mb-8">
        {/* Section header */}
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
              {MOCK_TODAY_APPOINTMENTS.map((appt) => (
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
                    {/* Placeholder for future action buttons */}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* ── Weekly summary ────────────────────────────────────────────────── */}
      <section>
        <div className="overflow-hidden rounded-xl border border-border">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-4 text-sm">
            <span className="font-bold uppercase tracking-wide text-foreground">
              Esta semana:
            </span>
            {MOCK_WEEKLY_SUMMARY.map((entry) => (
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
