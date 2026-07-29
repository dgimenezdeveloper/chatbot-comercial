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
    status: t.status || t.estado,
    // CORRECCIÓN: El backend envía 'nombre_cliente' y 'nombre_servicio'
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

  // Filtrar los turnos de "Hoy" ajustando a la zona horaria local (Ej: Argentina GMT-3)
  // para evitar que el UTC cambie de día antes de tiempo.
  const todayDate = new Date();
  const offset = todayDate.getTimezoneOffset() * 60000;
  const localISOTime = new Date(todayDate.getTime() - offset).toISOString().split("T")[0];
  
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