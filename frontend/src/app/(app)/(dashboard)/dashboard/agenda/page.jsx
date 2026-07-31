"use client";

import AgendaView from "@/components/features/agenda/agenda-view/agenda-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { ErrorState } from "@/components/ui/error-state/error-state";
import { useTurnos } from "@/hooks/useTurnos";
import { Loader2 } from "lucide-react";

/**
 * Mapeo de respaldo para traducir ID de servicio a su nombre descriptivo
 */
const SERVICE_NAMES = {
  1: "Corte de Cabello",
  2: "Tinte de Raíz",
  3: "Mechas Californianas",
  4: "Tratamiento Capilar",
  5: "Corte de Barba",
  6: "Peinado Profesional",
  7: "Alisado Brasileño",
  8: "Masaje Capilar",
};

/**
 * Mapea los turnos devueltos por el backend al formato visual que requiere la Agenda.
 */
function toAgendaAppointment(turno) {
  const date = turno.date || turno.fecha || new Date().toLocaleDateString("en-CA", { timeZone: "America/Argentina/Buenos_Aires" });
  const startTime = turno.startTime || turno.time || turno.hora || "09:00";
  let endTime = turno.endTime;

  if (!endTime) {
    const [hours, minutes] = startTime.split(":").map(Number);
    const duration = turno.durationMinutes || 30;
    const endMinutes = (minutes || 0) + duration;
    const endHours = (hours || 9) + Math.floor(endMinutes / 60);
    endTime = `${String(endHours).padStart(2, "0")}:${String(endMinutes % 60).padStart(2, "0")}`;
  }

  // 1. Extraer o construir el nombre del cliente de forma amigable
  let clientName =
    turno.clientName ||
    turno.nombre_cliente ||
    turno.user_name ||
    turno.client;

  const rawPhone = turno.phone || turno.telefono || turno.user_phone || "";

  if (!clientName || clientName === "Cliente" || clientName.startsWith("54911")) {
    if (rawPhone && rawPhone.length >= 4) {
      clientName = `Cliente ${rawPhone.slice(-4)}`;
    } else {
      clientName = "Cliente";
    }
  }

  // 2. Extraer o construir el nombre del servicio real
  const serviceId = turno.serviceId || turno.servicio_id;
  let serviceName =
    turno.serviceName ||
    turno.nombre_servicio ||
    turno.servicio_nombre ||
    turno.service;

  if (!serviceName || serviceName === "Servicio General" || serviceName.startsWith("Servicio #")) {
    serviceName = SERVICE_NAMES[serviceId] || (serviceId ? `Servicio #${serviceId}` : "Servicio General");
  }

  const rawStatus = turno.status || turno.estado || "confirmado";
  const isConfirmed = rawStatus === "confirmado" || rawStatus === "confirmed" || rawStatus === "completed";
  const isCancelled = rawStatus === "cancelado" || rawStatus === "cancelled";

  const statusTone = {
    confirmado: "green",
    confirmed: "green",
    completed: "green",
    pendiente: "purple",
    scheduled: "purple",
    cancelado: "gray",
    cancelled: "gray",
  };

  return {
    id: String(turno.id),
    clientName,
    serviceName,
    date,
    startTime,
    endTime,
    status: isConfirmed ? "confirmed" : isCancelled ? "cancelled" : "confirmed",
    tone: statusTone[rawStatus] || "green",
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

  // Filtrar turnos cancelados para que no ocupen espacio visual en la grilla de la agenda
  const activeTurnos = turnos.filter(t => t.status !== "cancelled" && t.status !== "cancelado");
  const appointments = activeTurnos.map(toAgendaAppointment);

  return (
    <DashboardPageLayout>
      <AgendaView appointments={appointments} initialDate={new Date()} />
    </DashboardPageLayout>
  );
}