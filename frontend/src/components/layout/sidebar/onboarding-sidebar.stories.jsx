import React from "react";

import {
  OnboardingProvider,
  useOnboarding,
} from "@/components/features/onboarding/shared/OnboardingContext";
import OnboardingSidebar from "./onboarding-sidebar";

const meta = {
  title: "Layout/Sidebar/OnboardingSidebar",
  component: OnboardingSidebar,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

function SidebarState({ currentStep }) {
  const { setStep } = useOnboarding();

  React.useEffect(() => {
    setStep(currentStep);
  }, [currentStep, setStep]);

  return (
    <div className="w-[280px]">
      <OnboardingSidebar />
    </div>
  );
}

function SidebarPreview({ currentStep }) {
  return (
    <OnboardingProvider>
      <SidebarState currentStep={currentStep} />
    </OnboardingProvider>
  );
}

export const BusinessActive = {
  render: () => <SidebarPreview currentStep={1} />,
};

export const ScheduleActive = {
  render: () => <SidebarPreview currentStep={2} />,
};