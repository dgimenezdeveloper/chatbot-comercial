import { auth } from "@/auth";
import AgendaView from "@/components/features/agenda/agenda-view/agenda-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";

async function fetchAppointments(token) {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${baseUrl}/calendar/turnos`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store", // Desactiva caché para ver agendamientos en tiempo real
    });

    if (!res.ok) {
      console.error(`Error obteniendo turnos (${res.status}):`, await res.text());
      return [];
    }
    return await res.json();
  } catch (error) {
    console.error("Error al conectar con el endpoint de turnos:", error);
    return [];
  }
}

export default async function AgendaPage() {
  const session = await auth();
  const appointments = await fetchAppointments(session?.backendAccessToken);

  return (
    <DashboardPageLayout>
      <AgendaView appointments={appointments} />
    </DashboardPageLayout>
  );
}