"use client";

import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";
import { MobileStepIndicator } from "@/components/layout/MobileStepIndicator";
import { ONBOARDING_STEPS } from "@/components/layout/sidebar/onboarding-sidebar";

/**
 * Thin client wrapper so the onboarding layout (Server Component)
 * can render MobileStepIndicator without reading context directly.
 * ONBOARDING_STEPS is the single source of truth imported from the sidebar.
 */
export function OnboardingMobileBar() {
  const { step } = useOnboarding();
  return <MobileStepIndicator currentStep={step} steps={ONBOARDING_STEPS} />;
}
