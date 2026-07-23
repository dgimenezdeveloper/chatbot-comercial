"use client";

import { useMemo } from "react";

/**
 * Hook que transforma los datos crudos del endpoint en formatos
 * listos para cada componente de gráfico.
 *
 * @param {Object|null} data - Respuesta completa del endpoint
 * @returns {{ funnelSteps, topFallbackData, topServicesData, nocturnalData, reminderData, kpis }}
 */
export function useMetricsData(data) {
  const topFallbackData = useMemo(() => {
    const msgs = data?.top_fallback_messages?.messages;
    if (!msgs?.length) return null;
    return msgs.map((m) => ({ name: m.message?.slice(0, 30) || "N/A", count: m.count }));
  }, [data]);

  const topServicesData = useMemo(() => {
    const svcs = data?.top_services?.services;
    if (!svcs?.length) return null;
    return svcs.map((s) => ({ name: s.service_name || `#${s.service_id}`, count: s.count }));
  }, [data]);

  const nocturnalData = useMemo(() => {
    const nr = data?.nocturnal_appointment_rate;
    if (!nr) return null;
    return [
      { name: "Nocturnos", value: nr.nocturnal_appointments || 0, fill: "#6366f1" },
      { name: "Diurnos", value: (nr.total_appointments || 0) - (nr.nocturnal_appointments || 0), fill: "#c7d2fe" },
    ];
  }, [data]);

  const newVsReturningData = useMemo(() => {
    const nv = data?.extended?.new_vs_returning;
    if (nv?.new_clients != null && nv?.total_clients != null && nv.total_clients > 0) {
      const newPct = Math.round((nv.new_clients / nv.total_clients) * 100);
      const returningPct = 100 - newPct;
      return [
        { name: "Nuevos", value: newPct, fill: "#6366f1" },
        { name: "Recurrentes", value: returningPct, fill: "#c7d2fe" },
      ];
    }
    return null;
  }, [data]);

  const hourlyDistributionData = useMemo(() => {
    const distrib = data?.extended?.message_hourly_distribution?.distribution;
    if (!distrib) return null;
    return Object.entries(distrib).map(([hour, count]) => ({ name: `${hour}h`, value: count }));
  }, [data]);

  const reminderData = useMemo(() => {
    const rc = data?.reminder_confirmation_rate;
    if (!rc) return null;
    return [
      { name: "Confirmaron", value: rc.confirmations || 0, fill: "#22c55e" },
      { name: "Sin respuesta", value: (rc.total_reminders || 0) - (rc.confirmations || 0), fill: "#e2e8f0" },
    ];
  }, [data]);

  const kpis = useMemo(() => {
    if (!data) return [];
    return [
      { title: "Conversión", value: `${data.conversion_rate?.value || 0}%`, status: data.conversion_rate?.status || "ok", trend: (data.conversion_rate?.value || 0) > 30 ? "up" : "down" },
      { title: "Autonomía", value: `${data.bot_autonomy_rate?.value || 0}%`, status: data.bot_autonomy_rate?.status || "ok", trend: (data.bot_autonomy_rate?.value || 0) > 50 ? "up" : "down" },
      { title: "No-Show", value: `${data.no_show_rate?.value || 0}%`, status: data.no_show_rate?.status || "ok", trend: (data.no_show_rate?.value || 0) < 10 ? "down" : "up" },
      { title: "CSAT", value: data.csat_average?.average_score?.toFixed(1) || "—", status: data.csat_average?.status || "ok", trend: (data.csat_average?.average_score || 0) >= 4 ? "up" : "down" },
      { title: "Fallback", value: `${data.fallback_rate?.value || 0}%`, status: data.fallback_rate?.status || "ok", trend: (data.fallback_rate?.value || 0) < 15 ? "down" : "up" },
    ];
  }, [data]);

  return { topFallbackData, topServicesData, nocturnalData, reminderData, kpis, newVsReturningData, hourlyDistributionData };
}