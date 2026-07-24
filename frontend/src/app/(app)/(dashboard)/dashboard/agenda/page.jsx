import AgendaView from "@/components/features/agenda/agenda-view/agenda-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { mockAppointments } from "@/lib/data-mock/mock-appointments";

export default function AgendaPage() {
  return (
    <DashboardPageLayout>
      <AgendaView appointments={mockAppointments} />
    </DashboardPageLayout>
  );
}
