/**
 * API service layer for /admin/negocio.
 *
 * @module services/negocio-api
 */

import apiClient from "@/lib/api-client";

// AGREGADA BARRA FINAL PARA EVITAR REDIRECCIÓN 307 DE FASTAPI EN AZURE
const ENDPOINT = "/admin/negocio/";

/**
 * Fetch business info.
 * Backend returns: { id, nombre, descripcion, horarios, contacto }
 * @returns {Promise<Object>}
 */
export async function fetchNegocio() {
  const { data } = await apiClient.get(ENDPOINT);
  return data;
}

/**
 * Update business info.
 * @param {{ nombre: string, descripcion: string, horarios: string, contacto: string }} payload
 * @returns {Promise<Object>}
 */
export async function updateNegocio(payload) {
  const { data } = await apiClient.put(ENDPOINT, payload);
  return data;
}