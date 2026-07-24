"use client";

import AgendaView from "@/components/features/agenda/agenda-view/agenda-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { useTurnos } from "@/hooks/useTurnos";
import { Loader2 } from "lucide-react";

/**
 * Maps turnos from useTurnos hook to the shape AgendaView expects.
 * AgendaView needs: { id, clientName, serviceName, date, startTime, endTime, status, tone }
 */
function toAgendaAppointment(turno) {
  // Estimate end time (default 45 min since backend doesn't provide duration)
  const [hours, minutes] = turno.time.split(":").map(Number);
  const endMinutes = minutes + 45;
  const endHours = hours + Math.floor(endMinutes / 60);
  const endTime = `${String(endHours).padStart(2, "0")}:${String(endMinutes % 60).padStart(2, "0")}`;

  const statusTone = {
    confirmado: "green",
    pendiente: "purple",
    cancelado: "gray",
  };

  return {
    id: String(turno.id),
    clientName: turno.clientName,
    serviceName: turno.serviceName,
    date: turno.date,
    startTime: turno.time,
    endTime,
    status: turno.status === "confirmado" ? "confirmed" : turno.status,
    tone: statusTone[turno.status] || "green",
  };
}

export default function AgendaPage() {
  const { turnos, isLoading, isError, error } = useTurnos();

  if (isLoading) {
    return (
      <DashboardPageLayout>
        <div className="flex flex-1 items-center justify-center py-20">
          <Loader2 className="size-8 animate-spin text-primary" />
          <span className="ml-3 text-sm text-muted-foreground">Cargando agenda...</span>
        </div>
      </DashboardPageLayout>
    );
  }

  if (isError) {
    return (
      <DashboardPageLayout>
        <div className="flex flex-1 items-center justify-center py-20">
          <p className="text-sm text-destructive">
            Error al cargar turnos: {error?.message || "Error desconocido"}
          </p>
        </div>
      </DashboardPageLayout>
    );
  }

  const appointments = turnos.map(toAgendaAppointment);

  return (
    <DashboardPageLayout>
      <AgendaView appointments={appointments} initialDate={new Date()} />
    </DashboardPageLayout>
  );
}
