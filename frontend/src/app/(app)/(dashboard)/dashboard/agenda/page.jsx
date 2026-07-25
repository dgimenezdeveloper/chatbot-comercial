"use client";

import AgendaView from "@/components/features/agenda/agenda-view/agenda-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { ErrorState } from "@/components/ui/error-state/error-state";
import { useTurnos } from "@/hooks/useTurnos";
import { Loader2 } from "lucide-react";

/**
 * Mapea los turnos del hook useTurnos al formato que espera AgendaView.
 */
function toAgendaAppointment(turno) {
  const startTime = turno.startTime || turno.time || "09:00";
  let endTime = turno.endTime;

  if (!endTime) {
    const [hours, minutes] = startTime.split(":").map(Number);
    const endMinutes = minutes + 45;
    const endHours = hours + Math.floor(endMinutes / 60);
    endTime = `${String(endHours).padStart(2, "0")}:${String(endMinutes % 60).padStart(2, "0")}`;
  }

  const statusTone = {
    confirmado: "green",
    confirmed: "green",
    pendiente: "purple",
    scheduled: "purple",
    cancelado: "gray",
    cancelled: "gray",
  };

  return {
    id: String(turno.id),
    clientName: turno.clientName || turno.client || "Cliente",
    serviceName: turno.serviceName || turno.service || "Servicio General",
    date: turno.date,
    startTime: startTime,
    endTime: endTime,
    status: (turno.status === "confirmado" || turno.status === "confirmed") ? "confirmed" : turno.status,
    tone: statusTone[turno.status] || "green",
  };
}

export default function AgendaPage() {
  const { turnos = [], isLoading, isError, error, refetch } = useTurnos();

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
        <ErrorState
          message={error?.message || "Ocurrió un error al cargar la agenda."}
          onRetry={refetch}
        />
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