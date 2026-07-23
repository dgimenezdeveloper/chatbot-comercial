"use client";

import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import Stepper from "@/components/ui/stepper/stepper";

import { AppSidebarShell } from "./app-sidebar-shell";

const STEPS = [
  {
    number: 1,
    label: "Tu Negocio",
  },
  {
    number: 2,
    label: "Horarios",
  },
];

export default function OnboardingSidebar() {
  const { step } = useOnboarding();

  return (
    <AppSidebarShell>
      <p className="mb-6 text-xs font-semibold uppercase tracking-wide text-sidebar-muted">
        Setup inicial
      </p>

      <Stepper steps={STEPS} currentStep={step} />
    </AppSidebarShell>
  );
}
