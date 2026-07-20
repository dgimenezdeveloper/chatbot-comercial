import { OnboardingProvider } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import OnboardingSidebar from "@/components/layout/sidebar/onborading-sidebar";

export default function OnboardingLayout({ children }) {
  return (
    <OnboardingProvider>
      <div className="flex min-h-screen bg-white">
        {/* Sidebar del onboarding */}
        <aside className="hidden w-[280px] shrink-0 lg:block">
          <OnboardingSidebar />
        </aside>

        {/* Contenido correspondiente al paso actual */}
        <main className="min-h-screen flex-1 overflow-y-auto p-8">
          <div className="mx-auto flex min-h-full max-w-[1200px] flex-col">
            {children}
          </div>
        </main>
      </div>
    </OnboardingProvider>
  );
}