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
  let url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

  // Auto-fix defensivo para navegador:
  // Si la página web corre sobre HTTPS y la URL configurada empieza con "http://" (y no es localhost),
  // forzamos el esquema a "https://" para prevenir el bloqueo por Mixed Content.
  if (
    typeof window !== "undefined" &&
    window.location.protocol === "https:" &&
    url.startsWith("http://") &&
    !url.includes("localhost")
  ) {
    url = url.replace("http://", "https://");
  }

  return url;
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

  // Construcción segura del objeto URL (soporta URLs absolutas y rutas relativas)
  const url = baseUrl.startsWith("/")
    ? new URL(baseUrl + "/admin/metrics", window.location.origin)
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