"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchServicios,
  createServicio,
  updateServicio,
  deleteServicio,
} from "@/services/servicios-api";

const SERVICIOS_KEY = ["servicios"];

function toFrontend(s) {
  return {
    id: s.id,
    name: s.nombre,
    description: s.descripcion || "",
    durationMinutes: s.duracion_minutos,
    basePrice: s.precio,
    active: s.activo ?? true,
    category: s.categoria || "General",
  };
}

function toBackend(s) {
  return {
    nombre: s.name,
    descripcion: s.description || null,
    duracion_minutos: s.durationMinutes,
    precio: s.basePrice,
    activo: s.active ?? true,
  };
}

export function useServicios() {
  const queryClient = useQueryClient();

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