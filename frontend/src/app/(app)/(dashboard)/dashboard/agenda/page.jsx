import AgendaView from "@/components/features/agenda/agenda-view/agenda-view";
import { mockAppointments } from "@/lib/data/mock-appointments";

export default function AgendaPage() {
  return <AgendaView appointments={mockAppointments} />;
}
