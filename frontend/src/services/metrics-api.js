/**
 * API service layer for /admin/metrics.
 *
 * Uses the shared Axios client with auto-injected auth token.
 * Replaces the legacy fetch-based api.js.
 *
 * @module services/metrics-api
 */

import apiClient from "@/lib/api-client";

/**
 * Fetch chatbot metrics for a business.
 *
 * @param {Object} params
 * @param {number} [params.days=30]
 * @param {number} [params.businessId=1]
 * @param {boolean} [params.includeExtended=false]
 * @param {string} [params.startDate]
 * @param {string} [params.endDate]
 * @param {string} [params.segmentBy]
 * @returns {Promise<Object>} Metrics response
 */
export async function fetchMetrics({
  days = 30,
  businessId = 1,
  includeExtended = false,
  startDate,
  endDate,
  segmentBy,
} = {}) {
  const params = {
    days,
    business_id: businessId,
  };

  if (includeExtended) params.include_extended = "true";
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (segmentBy) params.segment_by = segmentBy;

  const { data } = await apiClient.get("/admin/metrics/", { params });
  return data;
}
