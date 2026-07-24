import { auth } from "@/auth";
import ClientsView from "@/components/features/clients/clients-view/clients-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";

async function fetchClients(token) {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://pymebot.azurewebsites.net/api/v1";
  try {
    const headers = { "Content-Type": "application/json" };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${baseUrl}/admin/clientes`, {
      headers,
      cache: "no-store",
    });

    if (!res.ok) {
      console.error("Error obteniendo clientes:", await res.text());
      return { clients: [], totalCount: 0 };
    }
    return await res.json();
  } catch (error) {
    console.error("Error conectando con la API de clientes:", error);
    return { clients: [], totalCount: 0 };
  }
}

export default async function ClientesPage() {
  const session = await auth();
  const data = await fetchClients(session?.backendAccessToken);

  return (
    <DashboardPageLayout>
      <ClientsView clients={data.clients} totalCount={data.totalCount} />
    </DashboardPageLayout>
  );
}