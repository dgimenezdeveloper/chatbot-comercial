"use client";

import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import Stepper from "@/components/ui/stepper/stepper";

/**
 * Pasos visibles dentro del sidebar.
 */
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
    <aside className="flex min-h-screen flex-col border-r border-slate-200 bg-slate-50 px-8 py-10">
      {/* Logo temporal */}
      <div className="mb-12">
        <div className="flex h-16 items-center justify-center rounded-xl bg-blue-100">
          <span className="text-xl font-bold text-blue-700">
            PYMIO
          </span>
        </div>
      </div>

      <p className="mb-8 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Setup inicial
      </p>

      <Stepper
        steps={STEPS}
        currentStep={step}
      />
    </aside>
  );
}