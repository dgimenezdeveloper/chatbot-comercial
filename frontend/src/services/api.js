/**
 * Cliente HTTP para el endpoint de métricas del chatbot.
 *
 * GET /api/v1/admin/metrics?days=30&business_id=1
 *
 * @module services/api
 */

/**
 * Resuelve la URL base de forma inteligente.
 * En el navegador, utiliza una ruta relativa ("/api/v1") para que la petición 
 * viaje por el mismo dominio HTTPS de la página y sea reenviada internamente
 * por el proxy de Next.js (next.config.mjs), evitando errores de Mixed Content y CORS.
 */
const getBaseUrl = () => {
  // Si estamos en el navegador, usamos la ruta relativa del proxy de Next.js
  if (typeof window !== "undefined") {
    return "/api/v1";
  }
  // En SSR (Server-Side Rendering) de Node.js, usa la URL interna o fallback
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
};

/**
 * Obtiene métricas del chatbot para un negocio.
 *
 * @param {Object} params
 * @param {number} [params.days=30] 
 * @param {number} [params.businessId=1]  
 * @param {boolean} [params.includeExtended=false] 
 * @param {string} [params.startDate] 
 * @param {string} [params.endDate] 
 * @param {string} [params.segmentBy] 
 * @param {string} [params.accessToken] 
 * @returns {Promise<Object>} 
 * @throws {Error} 
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
  const baseUrl = getBaseUrl();

  // Construcción segura del objeto URL basada en el origen del navegador
  const url = baseUrl.startsWith("/")
    ? new URL(baseUrl + "/admin/metrics", typeof window !== "undefined" ? window.location.origin : "http://localhost:3000")
    : new URL(`${baseUrl}/admin/metrics`);

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

  const response = await fetch(url.toString(), { headers });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new Error(`Metrics fetch failed (${response.status}): ${errorText}`);
  }

  return response.json();
}