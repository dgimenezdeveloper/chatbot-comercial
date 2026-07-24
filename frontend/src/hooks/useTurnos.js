"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTurnos, createTurno, cancelTurno } from "@/services/turnos-api";

const TURNOS_KEY = ["turnos"];

/**
 * Normalizes backend turno shape to the frontend model.
 * Backend: { id, telefono, servicio_id, fecha, hora, estado }
 * Frontend: { id, phone, serviceId, date, time, status, clientName, serviceName }
 */
function toFrontend(t) {
  return {
    id: t.id,
    phone: t.telefono,
    serviceId: t.servicio_id,
    date: t.fecha,
    time: t.hora,
    status: t.estado,
    // Backend doesn't return these yet — provide placeholders
    clientName: t.cliente_nombre || t.telefono,
    serviceName: t.servicio_nombre || `Servicio #${t.servicio_id}`,
  };
}

/**
 * TanStack Query hook for Turnos.
 *
 * @returns {{
 *   turnos: Array,
 *   todayTurnos: Array,
 *   isLoading: boolean,
 *   isError: boolean,
 *   error: Error|null,
 *   refetch: Function,
 *   createAppointment: Function,
 *   cancelAppointment: Function,
 *   isCreating: boolean,
 *   isCancelling: boolean,
 * }}
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

  // Filter turnos for today
  const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
  const todayTurnos = turnos.filter((t) => t.date === today);

  // Mutations
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
