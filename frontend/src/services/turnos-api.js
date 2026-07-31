/**
 * API service layer for /calendar/turnos.
 *
 * @module services/turnos-api
 */

import apiClient from "@/lib/api-client";

// AGREGADA BARRA FINAL PARA EVITAR REDIRECCIÓN 307 DE FASTAPI EN AZURE
const ENDPOINT = "/calendar/turnos/";

/**
 * List all appointments.
 * Backend returns: [{ id, telefono, servicio_id, fecha, hora, estado }]
 * @returns {Promise<Array>}
 */
export async function fetchTurnos() {
  const { data } = await apiClient.get(ENDPOINT);
  return data;
}

/**
 * Create a new appointment.
 * @param {{ telefono: string, servicio_id: number, fecha: string, hora: string }} payload
 * @returns {Promise<Object>}
 */
export async function createTurno(payload) {
  const { data } = await apiClient.post(ENDPOINT, payload);
  return data;
}

/**
 * Cancel an appointment by ID.
 * @param {number} id
 * @returns {Promise<void>}
 */
export async function cancelTurno(id) {
  await apiClient.delete(`/calendar/turnos/${id}`);
}