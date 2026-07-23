"use client";

import { useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card/card";
import { MetricasIcon } from "@/components/icons/MetricasIcon";
import { Filter, RefreshCw } from "lucide-react";

import { useMetrics } from "@/hooks/useMetrics";
import { useMetricsFilter } from "@/hooks/useMetricsFilter";
import { useMetricsData } from "@/hooks/useMetricsData";
import { StaleBadge } from "@/components/ui/stale-badge/stale-badge";
import { EmptyState } from "@/components/ui/empty-state/empty-state";
import { MetricsKpiCard } from "@/components/ui/metrics-kpiCard/metrics-kpiCard";
import { MetricsPieChart } from "@/components/ui/metrics-pieChart/metrics-pieChart";
import { MetricsFunnelChart } from "@/components/ui/metrics-FunnelChart/metrics-FunnelChart";
import { MetricsGauge } from "@/components/ui/metrics-gauge/metrics-gauge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function MetricsHeader({ filters, setFilters, isStale, handleRefetch }) {
  return (
    <div className="sticky top-0 z-10 bg-slate-50/95 dark:bg-slate-900/95 backdrop-blur-sm border-b border-slate-200 dark:border-slate-800 -mx-6 -mt-6 px-8 py-6">
      <div className="flex items-center gap-4 mb-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-900/50 shadow-sm">
          <MetricasIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Métricas</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Dashboard de rendimiento y analytics</p>
        </div>
        <StaleBadge isStale={isStale} onRefresh={handleRefetch} />
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Período:</span>
          <div className="flex gap-2">
            {[7, 30, 90].map((period) => (
              <Button key={period} variant={filters.days === period ? "default" : "outline"} size="sm" onClick={() => setFilters({ days: period })}>
                {period === 7 ? "7 días" : period === 30 ? "30 días" : "90 días"}
              </Button>
            ))}
          </div>
        </div>
        <div className="ml-auto flex gap-2">
          <Button variant="outline" size="sm" onClick={handleRefetch}><RefreshCw className="h-4 w-4 mr-2" />Actualizar</Button>
        </div>
      </div>
    </div>
  );
}

export default function MetricsPage() {
  const { data: session } = useSession();
  const accessToken = session?.backendAccessToken;
  const { filters, setFilters } = useMetricsFilter({ days: 30, businessId: 1, includeExtended: true });
  const { data, loading, error, isStale, refetch } = useMetrics({ ...filters, accessToken });
  const { topFallbackData, topServicesData, nocturnalData, reminderData, kpis, newVsReturningData, hourlyDistributionData } = useMetricsData(data);

  const handleRefetch = useCallback(() => refetch(), [refetch]);

  if (error && !data) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader><CardTitle>Error al cargar métricas</CardTitle><CardDescription>{error.message}</CardDescription></CardHeader>
          <CardContent><Button onClick={handleRefetch}>Reintentar</Button></CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <MetricsHeader filters={filters} setFilters={setFilters} isStale={isStale} handleRefetch={handleRefetch} />
      <main className="mt-8 space-y-8">
        {/* KPI Cards */}
        <section className="bg-linear-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl shadow-lg shadow-indigo-500/20 p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white">Indicadores Clave de Rendimiento</h2>
            <p className="text-sm font-medium text-indigo-100 mt-1">Últimos {filters.days} días</p>
          </div>
          {loading && !data ? (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="h-28 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-xl" />)}</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">{kpis.map((kpi) => <MetricsKpiCard key={kpi.title} {...kpi} className="bg-white/20 backdrop-blur-sm border-white/30 shadow-lg" />)}</div>
          )}
        </section>

        {/* Fila 1: Funnel + Nuevos vs Recurrentes */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Conversión inicio → turno</CardTitle><CardDescription>Funnel de conversión</CardDescription></CardHeader>
            <CardContent className="min-h-87.5">{loading && !data ? <div className="h-64 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : data?.conversion_rate ? <MetricsFunnelChart steps={[{ label: `Conversaciones (${data.conversion_rate.starts || 0})`, value: data.conversion_rate.starts || 0, pct: 100 }, { label: `Turnos creados (${data.conversion_rate.appointments || 0})`, value: data.conversion_rate.appointments || 0, pct: data.conversion_rate.value || 0 }]} /> : <div className="flex items-center justify-center h-64"><EmptyState message="Sin datos de conversión disponibles" /></div>}</CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Clientes Nuevos vs Recurrentes</CardTitle><CardDescription>Distribución de usuarios</CardDescription></CardHeader>
            <CardContent className="min-h-87.5">{loading && !data ? <div className="h-64 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : <MetricsPieChart data={newVsReturningData || []} />}</CardContent>
          </Card>
        </section>

        {/* Fila 2: Fallbacks + Servicios */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Top 10 Fallbacks</CardTitle><CardDescription>Mensajes que el bot no entendió</CardDescription></CardHeader>
            <CardContent className="min-h-95">{loading && !data ? <div className="h-80 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : <MetricsPieChart data={(topFallbackData || []).map(f => ({ name: f.name, value: f.count }))} innerRadius={60} />}</CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Servicios Más Reservados</CardTitle><CardDescription>Ranking por volumen de turnos</CardDescription></CardHeader>
            <CardContent className="min-h-95">{loading && !data ? <div className="h-80 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : <MetricsPieChart data={(topServicesData || []).map(s => ({ name: s.name, value: s.count }))} innerRadius={60} />}</CardContent>
          </Card>
        </section>

        {/* Fila 3: Nocturnos + Recordatorios + Cancelaciones */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader><CardTitle>Turnos Nocturnos</CardTitle><CardDescription>Reservas entre 20hs y 8hs</CardDescription></CardHeader>
            <CardContent className="min-h-87.5">{loading && !data ? <div className="h-64 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : <MetricsPieChart data={nocturnalData || []} />}</CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Confirmación Recordatorio</CardTitle><CardDescription>Respuestas al T-24hs</CardDescription></CardHeader>
            <CardContent className="min-h-87.5">{loading && !data ? <div className="h-64 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : <MetricsPieChart data={reminderData || []} innerRadius={50} />}</CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Distribución Horaria</CardTitle><CardDescription>MENSAJES POR HORA (datos reales)</CardDescription></CardHeader>
            <CardContent>
              {loading && !data ? <div className="h-80 bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" />
              : hourlyDistributionData?.length > 0 ? (
                <div style={{ width: "100%", height: 320 }}>
                  <ResponsiveContainer>
                    <BarChart data={hourlyDistributionData} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#475569" }} />
                      <YAxis tick={{ fontSize: 11, fill: "#475569" }} />
                      <Tooltip contentStyle={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: "8px", fontSize: "13px", color: "#1e293b" }} />
                      <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-sm text-slate-400">Activar métricas extendidas para ver distribución horaria</div>
              )}
            </CardContent>
          </Card>
        </section>

        {/* Fila 4: Calidad del Bot */}
        <section>
          <Card>
            <CardHeader><CardTitle>Calidad del Bot</CardTitle><CardDescription>Tasa de fallback y resolución autónoma</CardDescription></CardHeader>
            <CardContent className="flex flex-wrap items-center justify-center gap-12 py-8">
              {loading && !data ? <div className="h-56 w-full bg-slate-200 dark:bg-slate-800 animate-pulse rounded-lg" /> : data ? <><div style={{ width: 200, height: 220 }}><MetricsGauge value={data.fallback_rate?.value || 0} status={data.fallback_rate?.status || "ok"} label="Tasa Fallback" height={220} /></div><div style={{ width: 200, height: 220 }}><MetricsGauge value={data.autonomous_resolution_rate?.value || 0} status={data.autonomous_resolution_rate?.status || "ok"} label="Resolución Autónoma" height={220} /></div></> : null}
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}