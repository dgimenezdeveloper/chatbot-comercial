"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchProductos,
  createProducto,
  updateProducto,
  deleteProducto,
} from "@/services/productos-api";

const PRODUCTOS_KEY = ["productos"];

function toFrontend(p) {
  return {
    id: p.id,
    name: p.nombre,
    description: p.descripcion || "",
    price: p.precio,
    stock: p.stock,
    active: p.activo ?? true,
  };
}

function toBackend(p) {
  return {
    nombre: p.name,
    descripcion: p.description || null,
    precio: p.price,
    stock: p.stock,
    activo: p.active ?? true,
  };
}

export function useProductos() {
  const queryClient = useQueryClient();

  const {
    data: products = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: PRODUCTOS_KEY,
    queryFn: fetchProductos,
    select: (data) => data.map(toFrontend),
  });

  const createMutation = useMutation({
    mutationFn: (productData) => createProducto(toBackend(productData)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PRODUCTOS_KEY }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, ...productData }) =>
      updateProducto(id, toBackend(productData)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PRODUCTOS_KEY }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => deleteProducto(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PRODUCTOS_KEY }),
  });

  return {
    products,
    isLoading,
    isError,
    error,
    refetch,
    createProduct: createMutation.mutate,
    updateProduct: updateMutation.mutate,
    deleteProduct: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}