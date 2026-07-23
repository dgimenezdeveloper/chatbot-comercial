"use client";

import { useState, useCallback } from "react";

/**
 * Hook para manejar filtros locales del dashboard de métricas.
 *
 * @param {Object} [defaults]
 * @param {number} [defaults.days=30]
 * @param {number} [defaults.businessId=1]
 * @param {boolean} [defaults.includeExtended=false]
 * @param {string} [defaults.startDate]
 * @param {string} [defaults.endDate]
 * @param {string} [defaults.segmentBy] - "service" | "channel"
 * @returns {{ filters: Object, setFilters: Function }}
 */
export function useMetricsFilter(defaults = {}) {
  const [filters, setFiltersState] = useState({
    days: defaults.days ?? 30,
    businessId: defaults.businessId ?? 1,
    includeExtended: defaults.includeExtended ?? false,
    startDate: defaults.startDate ?? undefined,
    endDate: defaults.endDate ?? undefined,
    segmentBy: defaults.segmentBy ?? undefined,
  });

  const setFilters = useCallback(
    (partial) => {
      setFiltersState((prev) => ({
        ...prev,
        ...partial,
      }));
    },
    [setFiltersState]
  );

  return { filters, setFilters };
}