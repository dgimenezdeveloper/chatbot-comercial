import apiClient from "@/lib/api-client";

const ENDPOINT = "/catalog/productos/";

export async function fetchProductos() {
  const { data } = await apiClient.get(ENDPOINT);
  return data;
}

export async function createProducto(payload) {
  const { data } = await apiClient.post(ENDPOINT, payload);
  return data;
}

export async function updateProducto(id, payload) {
  const { data } = await apiClient.put(`/catalog/productos/${id}`, payload);
  return data;
}

export async function deleteProducto(id) {
  await apiClient.delete(`/catalog/productos/${id}`);
}

export async function fetchPedidos() {
  const { data } = await apiClient.get(`${ENDPOINT}pedidos`);
  return data;
}

export async function updatePedidoEstado(id, estado) {
  const { data } = await apiClient.put(`${ENDPOINT}pedidos/${id}/estado`, { estado });
  return data;
}