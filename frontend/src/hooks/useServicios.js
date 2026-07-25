"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchServicios,
  createServicio,
  updateServicio,
  deleteServicio,
} from "@/services/servicios-api";

const SERVICIOS_KEY = ["servicios"];

/**
 * Normalizes backend service shape to the frontend model.
 * Backend: { id, nombre, descripcion, duracion_minutos, precio }
 * Frontend: { id, name, description, durationMinutes, basePrice, active }
 */
function toFrontend(s) {
  return {
    id: s.id,
    name: s.nombre,
    description: s.descripcion || "",
    durationMinutes: s.duracion_minutos,
    basePrice: s.precio,
    // Backend doesn't have active/category yet — default to true / "General"
    active: s.activo ?? true,
    category: s.categoria || "General",
  };
}

/**
 * Normalizes frontend shape to backend payload.
 */
function toBackend(s) {
  return {
    nombre: s.name,
    descripcion: s.description || null,
    duracion_minutos: s.durationMinutes,
    precio: s.basePrice,
  };
}

/**
 * TanStack Query hook for Servicios CRUD.
 *
 * @returns {{
 *   services: Array,
 *   isLoading: boolean,
 *   isError: boolean,
 *   error: Error|null,
 *   refetch: Function,
 *   createService: Function,
 *   updateService: Function,
 *   deleteService: Function,
 *   isCreating: boolean,
 *   isUpdating: boolean,
 *   isDeleting: boolean,
 * }}
 */
export function useServicios() {
  const queryClient = useQueryClient();

  // --- Query ---
  const {
    data: services = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: SERVICIOS_KEY,
    queryFn: fetchServicios,
    select: (data) => data.map(toFrontend),
  });

  // --- Mutations ---
  const createMutation = useMutation({
    mutationFn: (serviceData) => createServicio(toBackend(serviceData)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SERVICIOS_KEY }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, ...serviceData }) =>
      updateServicio(id, toBackend(serviceData)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SERVICIOS_KEY }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => deleteServicio(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SERVICIOS_KEY }),
  });

  return {
    services,
    isLoading,
    isError,
    error,
    refetch,
    createService: createMutation.mutate,
    updateService: updateMutation.mutate,
    deleteService: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
