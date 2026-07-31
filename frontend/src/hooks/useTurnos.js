"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTurnos, createTurno, cancelTurno } from "@/services/turnos-api";

const TURNOS_KEY = ["turnos"];

/**
 * Normaliza los datos del backend al formato del frontend.
 * Soporta tanto las keys en inglés de nuestro backend optimizado como las de fallback.
 */
function toFrontend(t) {
  return {
    id: t.id,
    phone: t.phone || t.telefono || "",
    serviceId: t.serviceId || t.servicio_id || 1,
    date: t.date || t.fecha, 
    time: t.startTime || t.hora, 
    startTime: t.startTime || t.hora,
    endTime: t.endTime,
    durationMinutes: t.durationMinutes || t.duracion_minutos || 30,
    status: t.status || t.estado,
    clientName: t.clientName || t.nombre_cliente || t.telefono || "Cliente",
    serviceName: t.serviceName || t.nombre_servicio || `Servicio #${t.servicio_id || 1}`,
    tone: t.tone || "green",
  };
}

/**
 * TanStack Query hook for Turnos.
 */
export function useTurnos() {
  const queryClient = useQueryClient();

  const {
    data: turnos = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: TURNOS_KEY,
    queryFn: fetchTurnos,
    select: (data) => data.map(toFrontend),
  });

  // Filtrar los turnos de "Hoy" en la zona horaria local del negocio (Argentina GMT-3)
  const localISOTime = new Date().toLocaleDateString("en-CA", { timeZone: "America/Argentina/Buenos_Aires" });
  
  const todayTurnos = turnos.filter((t) => t.date === localISOTime);

  // Mutaciones
  const createMutation = useMutation({
    mutationFn: (payload) => createTurno(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TURNOS_KEY }),
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => cancelTurno(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TURNOS_KEY }),
  });

  return {
    turnos,
    todayTurnos,
    isLoading,
    isError,
    error,
    refetch,
    createAppointment: createMutation.mutate,
    cancelAppointment: cancelMutation.mutate,
    isCreating: createMutation.isPending,
    isCancelling: cancelMutation.isPending,
  };
}