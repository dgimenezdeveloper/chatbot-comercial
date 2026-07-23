"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { fetchMetrics } from "@/services/api";

/**
 * Hook principal de métricas. Maneja fetch, caché, polling y estados.
 *
 * @param {Object} filters - Filtros desde useMetricsFilter (incluye accessToken opcional)
 * @param {number} filters.days
 * @param {number} filters.businessId
 * @param {boolean} filters.includeExtended
 * @param {string} [filters.startDate]
 * @param {string} [filters.endDate]
 * @param {string} [filters.segmentBy]
 * @param {string} [filters.accessToken] - Token backend (desde session)
 * @returns {{ data: Object|null, loading: boolean, error: Error|null, isStale: boolean, refetch: Function }}
 */
export function useMetrics(filters) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isStale, setIsStale] = useState(false);

  const cachedData = useRef(null);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);
  const inflightRef = useRef(false);

  const doFetch = useCallback(
    async (showLoading = true) => {
      // Prevent concurrent requests (race condition fix)
      if (inflightRef.current) return;
      inflightRef.current = true;

      if (showLoading) setLoading(true);
      setError(null);

      try {
        const { accessToken, days, businessId, includeExtended, startDate, endDate, segmentBy } = filters;
        const result = await fetchMetrics({
          days, businessId, includeExtended, startDate, endDate, segmentBy,
          accessToken,
        });
        cachedData.current = result;
        // Guard against unmounted component state update
        if (mountedRef.current) {
          setData(result);
          setIsStale(false);
        }
      } catch (err) {
        if (cachedData.current) {
          if (mountedRef.current) {
            setData(cachedData.current);
            setIsStale(true);
          }
        } else if (mountedRef.current) {
          setError(err);
        }
      } finally {
        if (showLoading && mountedRef.current) setLoading(false);
        inflightRef.current = false;
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [filters.days, filters.businessId, filters.includeExtended, filters.startDate, filters.endDate, filters.segmentBy, filters.accessToken]
  );

  // Fetch inicial + re-fetch cuando cambian los filtros
  useEffect(() => {
    doFetch(true);
  }, [doFetch]);

  // Polling inteligente con Page Visibility API
  useEffect(() => {
    mountedRef.current = true;

    const startPolling = () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(() => {
        if (document.visibilityState === "visible" && !inflightRef.current) {
          doFetch(false);
        }
      }, 60_000);
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        doFetch(false);
        startPolling();
      } else {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    startPolling();

    return () => {
      mountedRef.current = false;
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [doFetch]);

  const refetch = useCallback(() => {
    doFetch(true);
  }, [doFetch]);

  return { data, loading, error, isStale, refetch };
}