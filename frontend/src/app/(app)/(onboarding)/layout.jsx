import { OnboardingProvider } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import { OnboardingMobileBar } from "@/components/features/onboarding/shared/OnboardingMobileBar";
import { OnboardingGuard } from "@/components/guards/OnboardingGuard";
import OnboardingSidebar from "@/components/layout/sidebar/onboarding-sidebar";
import AppShell from "@/components/layout/AppShell";

export default function OnboardingLayout({ children }) {
  return (
    <OnboardingGuard requireCompleted>
      <OnboardingProvider>
        <AppShell
          sidebar={<OnboardingSidebar />}
          topBar={<OnboardingMobileBar />}
        >
          <div className="mx-auto flex min-h-full max-w-[1200px] flex-col p-6 lg:p-8">
            {children}
          </div>
        </AppShell>
      </OnboardingProvider>
    </OnboardingGuard>
  );
}
