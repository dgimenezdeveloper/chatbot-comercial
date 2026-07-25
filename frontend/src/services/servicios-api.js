/**
 * API service layer for /catalog/servicios CRUD.
 *
 * All functions return the response data directly (Axios unwrap).
 * Auth is handled automatically by the apiClient interceptor.
 *
 * Backend shape (response):
 *   { id: number, nombre: string, descripcion: string|null, duracion_minutos: number, precio: number }
 *
 * @module services/servicios-api
 */

import apiClient from "@/lib/api-client";

// AGREGADA BARRA FINAL PARA EVITAR REDIRECCIÓN 307 DE FASTAPI EN AZURE
const ENDPOINT = "/catalog/servicios/";

/**
 * List all services for the authenticated business.
 * @returns {Promise<Array>} List of service objects
 */
export async function fetchServicios() {
  const { data } = await apiClient.get(ENDPOINT);
  return data;
}

/**
 * Create a new service.
 * @param {{ nombre: string, duracion_minutos: number, precio: number, descripcion?: string }} payload
 * @returns {Promise<Object>} Created service
 */
export async function createServicio(payload) {
  const { data } = await apiClient.post(ENDPOINT, payload);
  return data;
}

/**
 * Update an existing service.
 * @param {number} id - Service ID
 * @param {{ nombre: string, duracion_minutos: number, precio: number, descripcion?: string }} payload
 * @returns {Promise<Object>} Updated service
 */
export async function updateServicio(id, payload) {
  const { data } = await apiClient.put(`/catalog/servicios/${id}`, payload);
  return data;
}

/**
 * Delete a service by ID.
 * @param {number} id - Service ID
 * @returns {Promise<void>}
 */
export async function deleteServicio(id) {
  await apiClient.delete(`/catalog/servicios/${id}`);
}