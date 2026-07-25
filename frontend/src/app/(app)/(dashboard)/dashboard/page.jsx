"use client";

import { Loader2, Plus, LayoutDashboard } from "lucide-react";
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
import { useTurnos } from "@/hooks/useTurnos";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  confirmado:      { label: "Confirmado",        className: "bg-success/15 text-success border border-success/30" },
  confirmed:       { label: "Confirmado",        className: "bg-success/15 text-success border border-success/30" },
  pendiente:       { label: "Pendiente",         className: "bg-warning/15 text-warning-foreground border border-warning/40" },
  pending_deposit: { label: "Pendiente de Seña", className: "bg-warning/15 text-warning-foreground border border-warning/40" },
  cancelado:       { label: "Cancelado",         className: "bg-destructive/10 text-destructive border border-destructive/30" },
  expired:         { label: "Expirado",          className: "bg-destructive/10 text-destructive border border-destructive/30" },
  unassigned:      { label: "Sin Asignar",       className: "bg-muted text-muted-foreground border border-border" },
};

function StatCard({ value, label, isLoading }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 rounded-xl border border-border bg-card px-6 py-5 text-center">
      {isLoading ? (
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      ) : (
        <span className="text-3xl font-bold text-foreground">{value}</span>
      )}
      <span className="text-sm text-muted-foreground">{label}</span>
    </div>
  );
}

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? {
    label: status || "—",
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

export default function DashboardPage() {
  const { turnos = [], todayTurnos = [], isLoading } = useTurnos();

  return (
    <DashboardPageLayout>
      <PageHeader
        icon={<LayoutDashboard className="size-5" />}
        title="Panel de Control"
      />

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          value={todayTurnos.length}
          label="Turnos Hoy"
          isLoading={isLoading}
        />
        <StatCard
          value={`$${(0).toLocaleString("es-AR")}`}
          label="Señas cobradas"
          isLoading={isLoading}
        />
        <StatCard
          value={turnos.length}
          label="Turnos totales"
          isLoading={isLoading}
        />
        <StatCard
          value={todayTurnos.filter((t) => t.status === "confirmado" || t.status === "confirmed").length}
          label="Confirmados hoy"
          isLoading={isLoading}
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
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="px-5 py-10 text-center">
                    <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ) : todayTurnos.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="px-5 py-10 text-center text-muted-foreground">
                    No hay turnos programados para hoy.
                  </TableCell>
                </TableRow>
              ) : (
                todayTurnos.map((turno) => (
                  <TableRow key={turno.id} className="border-border hover:bg-muted/30">
                    <TableCell className="px-5 py-4 font-medium text-foreground">
                      {turno.startTime || turno.time}
                    </TableCell>
                    <TableCell className="px-5 py-4 text-foreground">
                      {turno.clientName}
                    </TableCell>
                    <TableCell className="px-5 py-4 text-muted-foreground">
                      {turno.serviceName}
                    </TableCell>
                    <TableCell className="px-5 py-4">
                      <StatusBadge status={turno.status} />
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
              Resumen:
            </span>
            <span className="flex items-baseline gap-1.5">
              <span className="text-muted-foreground">Total:</span>
              <span className="font-bold text-foreground">{isLoading ? "..." : turnos.length}</span>
            </span>
            <span className="flex items-baseline gap-1.5">
              <span className="text-muted-foreground">Confirmados:</span>
              <span className="font-bold text-foreground">
                {isLoading ? "..." : turnos.filter((t) => t.status === "confirmado" || t.status === "confirmed").length}
              </span>
            </span>
            <span className="flex items-baseline gap-1.5">
              <span className="text-muted-foreground">Pendientes:</span>
              <span className="font-bold text-foreground">
                {isLoading ? "..." : turnos.filter((t) => t.status === "pendiente" || t.status === "scheduled").length}
              </span>
            </span>
          </div>
        </div>
      </section>
    </DashboardPageLayout>
  );
}