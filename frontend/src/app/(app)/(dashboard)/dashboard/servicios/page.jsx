import { auth } from "@/auth";
import ServicesView from "@/components/features/services/services-view/services-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";

export default async function ServiciosPage() {
  const session = await auth();
  const token = session?.backendAccessToken;

  let services = [];

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL
      ? `${process.env.NEXT_PUBLIC_API_URL}/catalog/servicios/`
      : "http://localhost:8000/api/v1/catalog/servicios/";

    const res = await fetch(apiUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      services = data.map((s) => ({
        id: String(s.id),
        name: s.nombre,
        category: "General",
        durationMinutes: s.duracion_minutos,
        basePrice: s.precio,
        active: true,
      }));
    }
  } catch (error) {
    console.error("Error al obtener servicios:", error);
  }

  return (
    <DashboardPageLayout>
      <ServicesView services={services} />
    </DashboardPageLayout>
  );
}