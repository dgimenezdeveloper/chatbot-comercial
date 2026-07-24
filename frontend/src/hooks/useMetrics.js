"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchMetrics } from "@/services/metrics-api";

const METRICS_KEY = "metrics";

/**
 * TanStack Query hook for chatbot metrics.
 *
 * Replaces the legacy manual fetch/cache/polling implementation.
 * Features provided by TanStack Query out of the box:
 *   - Automatic caching and deduplication
 *   - Refetch on window focus
 *   - Background polling (refetchInterval)
 *   - Stale/fresh state management
 *
 * @param {Object} filters
 * @param {number} filters.days
 * @param {number} filters.businessId
 * @param {boolean} filters.includeExtended
 * @param {string} [filters.startDate]
 * @param {string} [filters.endDate]
 * @param {string} [filters.segmentBy]
 * @returns {{ data: Object|null, loading: boolean, error: Error|null, isStale: boolean, refetch: Function }}
 */
export function useMetrics(filters) {
  const {
    days,
    businessId,
    includeExtended,
    startDate,
    endDate,
    segmentBy,
  } = filters;

  const {
    data = null,
    isLoading,
    isFetching,
    isError,
    error,
    isStale,
    refetch,
  } = useQuery({
    queryKey: [METRICS_KEY, { days, businessId, includeExtended, startDate, endDate, segmentBy }],
    queryFn: () => fetchMetrics({ days, businessId, includeExtended, startDate, endDate, segmentBy }),
    staleTime: 60 * 1000,           // 1 min fresh
    refetchInterval: 60 * 1000,     // Poll every 60s (replaces manual setInterval)
    refetchOnWindowFocus: true,     // Replaces manual visibility API
    retry: 1,
    placeholderData: (prev) => prev, // Keep previous data while refetching (replaces manual cache)
  });

  return {
    data,
    loading: isLoading,
    error: isError ? error : null,
    isStale: isStale && !isFetching,
    refetch,
  };
}
