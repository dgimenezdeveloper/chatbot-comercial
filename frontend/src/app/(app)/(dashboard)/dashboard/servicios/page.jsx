import ServicesView from "@/components/features/services/services-view/services-view";
import { mockServices } from "@/lib/data/mock-services";

export default function ServiciosPage() {
  return <ServicesView services={mockServices} />;
}
