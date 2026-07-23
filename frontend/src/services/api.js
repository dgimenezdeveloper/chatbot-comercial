/**
 * Cliente HTTP para el endpoint de métricas del chatbot.
 *
 * GET /api/v1/admin/metrics?days=30&business_id=1
 *
 * @module services/api
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Obtiene métricas del chatbot para un negocio.
 *
 * @param {Object} params
 * @param {number} [params.days=30] - Días hacia atrás para calcular métricas
 * @param {number} [params.businessId=1] - ID del negocio
 * @param {boolean} [params.includeExtended=false] - Incluir 38 métricas extendidas
 * @param {string} [params.startDate] - Fecha inicio (YYYY-MM-DD). Precede a days
 * @param {string} [params.endDate] - Fecha fin (YYYY-MM-DD). Precede a days
 * @param {string} [params.segmentBy] - Segmentar por: "service" | "channel"
 * @param {string} [params.accessToken] - Token de acceso backend (desde session)
 * @returns {Promise<Object>} Respuesta JSON con métricas
 * @throws {Error} Si la request falla o retorna status no-ok
 */
export async function fetchMetrics({
  days = 30,
  businessId = 1,
  includeExtended = false,
  startDate,
  endDate,
  segmentBy,
  accessToken,
} = {}) {
  const url = new URL(`${BASE_URL}/admin/metrics`);

  url.searchParams.set("days", days);
  url.searchParams.set("business_id", businessId);

  if (includeExtended) {
    url.searchParams.set("include_extended", "true");
  }
  if (startDate) {
    url.searchParams.set("start_date", startDate);
  }
  if (endDate) {
    url.searchParams.set("end_date", endDate);
  }
  if (segmentBy) {
    url.searchParams.set("segment_by", segmentBy);
  }

  const headers = { "Content-Type": "application/json" };
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, { headers });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new Error(`Metrics fetch failed (${response.status}): ${errorText}`);
  }

  return response.json();
}