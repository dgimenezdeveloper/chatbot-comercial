"use client";

import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import Stepper from "@/components/ui/stepper/stepper";
import { AppSidebarShell } from "./app-sidebar-shell";

// Steps definition shared with OnboardingMobileBar
export const ONBOARDING_STEPS = [
  { number: 1, label: "Tu Negocio" },
  { number: 2, label: "Horarios" },
];

export default function OnboardingSidebar() {
  const { step } = useOnboarding();

  return (
    <AppSidebarShell>
      {/* "Setup inicial" label */}
      <p className="mb-6 text-xs font-semibold uppercase tracking-wide text-sidebar-muted">
        Setup inicial
      </p>

      {/* Vertical stepper — circles + connecting line */}
      <Stepper steps={ONBOARDING_STEPS} currentStep={step} />
    </AppSidebarShell>
  );
}
