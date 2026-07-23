import { OnboardingProvider } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import OnboardingSidebar from "@/components/layout/sidebar/onboarding-sidebar";

export default function OnboardingLayout({ children }) {
  return (
    <OnboardingProvider>
      <div className="flex min-h-screen bg-surface">
        <div className="hidden shrink-0 lg:block">
          <OnboardingSidebar />
        </div>

        <main className="min-h-screen flex-1 overflow-y-auto p-8">
          <div className="mx-auto flex min-h-full max-w-[1200px] flex-col">
            {children}
          </div>
        </main>
      </div>
    </OnboardingProvider>
  );
}