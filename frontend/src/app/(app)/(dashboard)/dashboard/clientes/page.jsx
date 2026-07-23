import ClientsView from "@/components/features/clients/clients-view/clients-view";
import {
  mockClients,
  MOCK_CLIENTS_TOTAL,
} from "@/lib/data/mock-clients";

export default function ClientesPage() {
  return (
    <ClientsView clients={mockClients} totalCount={MOCK_CLIENTS_TOTAL} />
  );
}
