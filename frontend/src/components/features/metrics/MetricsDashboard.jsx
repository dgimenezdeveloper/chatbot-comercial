"use client";

import { useCallback } from "react";
import { Filter, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card/card";
import { MetricasIcon } from "@/components/icons/MetricasIcon";
import { StaleBadge } from "@/components/ui/stale-badge/stale-badge";
import { EmptyState } from "@/components/ui/empty-state/empty-state";
import { MetricsKpiCard } from "@/components/ui/metrics-kpiCard/metrics-kpiCard";
import { MetricsPieChart } from "@/components/ui/metrics-pieChart/metrics-pieChart";
import { MetricsFunnelChart } from "@/components/ui/metrics-FunnelChart/metrics-FunnelChart";
import { MetricsGauge } from "@/components/ui/metrics-gauge/metrics-gauge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { useMetrics } from "@/hooks/useMetrics";
import { useMetricsFilter } from "@/hooks/useMetricsFilter";
import { useMetricsData } from "@/hooks/useMetricsData";

function Skeleton({ className }) {
  return <div className={cn("animate-pulse rounded-lg bg-muted", className)} />;
}

function PeriodFilter({ filters, setFilters, isStale, onRefetch }) {
  return (
    <div className="mb-6 flex flex-wrap items-center gap-4">
      <div className="flex items-center gap-2">
        <Filter className="size-4 text-muted-foreground" />
        <span className="text-sm font-medium text-foreground">Período:</span>
        <div className="flex gap-2">
          {[7, 30, 90].map((period) => (
            <Button
              key={period}
              variant={filters.days === period ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({ days: period })}
            >
              {period === 7 ? "7 días" : period === 30 ? "30 días" : "90 días"}
            </Button>
          ))}
        </div>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <StaleBadge isStale={isStale} onRefresh={onRefetch} />
        <Button variant="outline" size="sm" onClick={onRefetch}>
          <RefreshCw className="size-4" />
          Actualizar
        </Button>
      </div>
    </div>
  );
}

export function MetricsDashboard({ accessToken, businessId = 1 }) {
  const { filters, setFilters } = useMetricsFilter({
    days: 30,
    businessId: businessId,  // Leído desde la sesión del usuario
    includeExtended: true,
  });

  const { data, loading, error, isStale, refetch } = useMetrics({
    ...filters,
    accessToken,
  });

  const {
    topFallbackData,
    topServicesData,
    nocturnalData,
    reminderData,
    kpis,
    newVsReturningData,
    hourlyDistributionData,
  } = useMetricsData(data);

  const handleRefetch = useCallback(() => refetch(), [refetch]);

  if (error && !data) {
    return (
      <DashboardPageLayout>
        <PageHeader
          icon={<MetricasIcon className="size-5" />}
          title="Métricas"
        />
        <div className="flex flex-1 items-center justify-center">
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle>Error al cargar métricas</CardTitle>
              <CardDescription>{error.message}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={handleRefetch}>Reintentar</Button>
            </CardContent>
          </Card>
        </div>
      </DashboardPageLayout>
    );
  }

  return (
    <DashboardPageLayout>
      <PageHeader
        icon={<MetricasIcon className="size-5" />}
        title="Métricas"
      />

      <PeriodFilter
        filters={filters}
        setFilters={setFilters}
        isStale={isStale}
        onRefetch={handleRefetch}
      />

      <div className="space-y-8">
        {/* KPI Cards */}
        <section className="rounded-2xl p-6 shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-semibold">
              Indicadores Clave de Rendimiento
            </h2>
            <p className="mt-0.5 text-sm text-primary-foreground/70">
              Últimos {filters.days} días
            </p>
          </div>
          {loading && !data ? (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-28 animate-pulse rounded-xl bg-primary-foreground/20" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
              {kpis.map((kpi) => (
                <MetricsKpiCard
                  key={kpi.title}
                  {...kpi}
                  className="border-primary-foreground/20 bg-primary-foreground/15 backdrop-blur-sm"
                />
              ))}
            </div>
          )}
        </section>

        {/* Funnel + Nuevos vs Recurrentes */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Conversión inicio → turno</CardTitle>
              <CardDescription>Funnel de conversión</CardDescription>
            </CardHeader>
            <CardContent className="min-h-[22rem]">
              {loading && !data ? (
                <Skeleton className="h-64 w-full" />
              ) : data?.conversion_rate ? (
                <MetricsFunnelChart
                  steps={[
                    { label: `Conversaciones (${data.conversion_rate.starts || 0})`, value: data.conversion_rate.starts || 0, pct: 100 },
                    { label: `Turnos creados (${data.conversion_rate.appointments || 0})`, value: data.conversion_rate.appointments || 0, pct: data.conversion_rate.value || 0 },
                  ]}
                />
              ) : (
                <div className="flex h-64 items-center justify-center">
                  <EmptyState message="Sin datos de conversión disponibles" />
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Clientes Nuevos vs Recurrentes</CardTitle>
              <CardDescription>Distribución de usuarios</CardDescription>
            </CardHeader>
            <CardContent className="min-h-[22rem]">
              {loading && !data ? (
                <Skeleton className="h-64 w-full" />
              ) : (
                <MetricsPieChart data={newVsReturningData || []} />
              )}
            </CardContent>
          </Card>
        </section>

        {/* Fallbacks + Servicios */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Top 10 Fallbacks</CardTitle>
              <CardDescription>Mensajes que el bot no entendió</CardDescription>
            </CardHeader>
            <CardContent className="min-h-[24rem]">
              {loading && !data ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <MetricsPieChart
                  data={(topFallbackData || []).map((f) => ({ name: f.name, value: f.count }))}
                  innerRadius={60}
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Servicios Más Reservados</CardTitle>
              <CardDescription>Ranking por volumen de turnos</CardDescription>
            </CardHeader>
            <CardContent className="min-h-[24rem]">
              {loading && !data ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <MetricsPieChart
                  data={(topServicesData || []).map((s) => ({ name: s.name, value: s.count }))}
                  innerRadius={60}
                />
              )}
            </CardContent>
          </Card>
        </section>

        {/* Nocturnos + Recordatorios + Distribución Horaria */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Turnos Nocturnos</CardTitle>
              <CardDescription>Reservas entre 20hs y 8hs</CardDescription>
            </CardHeader>
            <CardContent className="min-h-[22rem]">
              {loading && !data ? <Skeleton className="h-64 w-full" /> : <MetricsPieChart data={nocturnalData || []} />}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Confirmación Recordatorio</CardTitle>
              <CardDescription>Respuestas al T-24hs</CardDescription>
            </CardHeader>
            <CardContent className="min-h-[22rem]">
              {loading && !data ? <Skeleton className="h-64 w-full" /> : <MetricsPieChart data={reminderData || []} innerRadius={50} />}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Distribución Horaria</CardTitle>
              <CardDescription>Mensajes por hora</CardDescription>
            </CardHeader>
            <CardContent>
              {loading && !data ? (
                <Skeleton className="h-80 w-full" />
              ) : hourlyDistributionData?.length > 0 ? (
                <div style={{ width: "100%", height: 320 }}>
                  <ResponsiveContainer>
                    <BarChart data={hourlyDistributionData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="name" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
                      <YAxis tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
                      <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "13px", color: "hsl(var(--foreground))" }} />
                      <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center">
                  <EmptyState message="Activar métricas extendidas para ver distribución horaria" />
                </div>
              )}
            </CardContent>
          </Card>
        </section>

        {/* Calidad del Bot */}
        <section>
          <Card>
            <CardHeader>
              <CardTitle>Calidad del Bot</CardTitle>
              <CardDescription>Tasa de fallback y resolución autónoma</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap items-center justify-center gap-12 py-8">
              {loading && !data ? (
                <Skeleton className="h-56 w-full" />
              ) : data ? (
                <>
                  <div style={{ width: 200, height: 220 }}>
                    <MetricsGauge value={data.fallback_rate?.value || 0} status={data.fallback_rate?.status || "ok"} label="Tasa Fallback" height={220} />
                  </div>
                  <div style={{ width: 200, height: 220 }}>
                    <MetricsGauge value={data.autonomous_resolution_rate?.value || 0} status={data.autonomous_resolution_rate?.status || "ok"} label="Resolución Autónoma" height={220} />
                  </div>
                </>
              ) : null}
            </CardContent>
          </Card>
        </section>
      </div>
    </DashboardPageLayout>
  );
}