import ClientsView from "@/components/features/clients/clients-view/clients-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { mockClients, MOCK_CLIENTS_TOTAL } from "@/lib/data-mock/mock-clients";

export default function ClientesPage() {
  return (
    <DashboardPageLayout>
      <ClientsView clients={mockClients} totalCount={MOCK_CLIENTS_TOTAL} />
    </DashboardPageLayout>
  );
}
