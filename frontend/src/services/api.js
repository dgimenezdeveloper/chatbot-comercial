/**
 * Cliente HTTP para el endpoint de métricas del chatbot.
 *
 * GET /api/v1/admin/metrics?days=30&business_id=1
 *
 * @module services/api
 */

/**
 * Resuelve y sanitiza la URL base de la API.
 * Garantiza que en entornos de producción con HTTPS no se realicen peticiones HTTP inseguras (evita Mixed Content).
 */
const getBaseUrl = () => {
  if (typeof window !== "undefined") {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    
    if (envUrl) {
      // Si la variable de entorno viene con "http://" en una página que corre en HTTPS,
      // la corregimos automáticamente a "https://" en el cliente.
      if (window.location.protocol === "https:" && envUrl.startsWith("http://") && !envUrl.includes("localhost")) {
        return envUrl.replace("http://", "https://");
      }
      return envUrl;
    }
    // Fallback seguro: usar ruta relativa para aprovechar el proxy invisible de next.config.mjs
    return "/api/v1";
  }

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

  // Si baseUrl es relativa (ej: /api/v1), la combinamos de forma segura con el origen actual del navegador
  const url = baseUrl.startsWith("/")
    ? new URL(baseUrl + "/admin/metrics", typeof window !== "undefined" ? window.location.origin : "http://localhost:3000")
    : new URL(`${baseUrl}/admin/metrics`);

  // Aseguramiento estricto de protocolo HTTPS en el navegador
  if (
    typeof window !== "undefined" &&
    window.location.protocol === "https:" &&
    url.protocol === "http:" &&
    !url.hostname.includes("localhost")
  ) {
    url.protocol = "https:";
  }

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