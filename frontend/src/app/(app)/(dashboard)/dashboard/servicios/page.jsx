"use client";

import ServicesView from "@/components/features/services/services-view/services-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { useServicios } from "@/hooks/useServicios";

export default function ServiciosPage() {
  const {
    services,
    isLoading,
    isError,
    error,
    refetch,
    deleteService,
  } = useServicios();

  return (
    <DashboardPageLayout>
      <ServicesView
        services={services}
        isLoading={isLoading}
        isError={isError}
        error={error}
        onRetry={refetch}
        onDeleteService={deleteService}
      />
    </DashboardPageLayout>
  );
}
