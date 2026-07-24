import ServicesView from "@/components/features/services/services-view/services-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { mockServices } from "@/lib/data/mock-services";

export default function ServiciosPage() {
  return (
    <DashboardPageLayout>
      <ServicesView services={mockServices} />
    </DashboardPageLayout>
  );
}
