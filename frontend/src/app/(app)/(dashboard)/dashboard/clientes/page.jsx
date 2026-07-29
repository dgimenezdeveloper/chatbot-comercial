import { auth } from "@/auth";
import ClientsView from "@/components/features/clients/clients-view/clients-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";

export default async function ClientesPage() {
  const session = await auth();
  const token = session?.backendAccessToken;

  let clients = [];

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL
      ? `${process.env.NEXT_PUBLIC_API_URL}/admin/negocio/clientes`
      : "http://localhost:8000/api/v1/admin/negocio/clientes";

    const res = await fetch(apiUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });

    if (res.ok) {
      clients = await res.json();
    }
  } catch (error) {
    console.error("Error al obtener clientes:", error);
  }

  return (
    <DashboardPageLayout>
      <ClientsView clients={clients} totalCount={clients.length} />
    </DashboardPageLayout>
  );
}