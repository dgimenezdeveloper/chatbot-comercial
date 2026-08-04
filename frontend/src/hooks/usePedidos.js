"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchPedidos, updatePedidoEstado } from "@/services/productos-api";

export function usePedidos() {
  const queryClient = useQueryClient();

  const {
    data: pedidos = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["pedidos"],
    queryFn: fetchPedidos,
    refetchInterval: 5000,
  });

  const updateEstadoMutation = useMutation({
    mutationFn: ({ id, estado }) => updatePedidoEstado(id, estado),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pedidos"] }),
  });

  return {
    pedidos,
    isLoading,
    isError,
    error,
    refetch,
    updateEstado: updateEstadoMutation.mutate,
    isUpdating: updateEstadoMutation.isPending,
  };
}