"use client";

import { createContext, useContext, useState } from "react";

/**
 * Contexto utilizado para compartir el paso actual
 * entre la página del onboarding y el sidebar.
 */
const OnboardingContext = createContext(null);

export function OnboardingProvider({ children }) {
  const [step, setStep] = useState(1);

  return (
    <OnboardingContext.Provider value={{ step, setStep }}>
      {children}
    </OnboardingContext.Provider>
  );
}

/**
 * Hook para acceder al paso actual del onboarding.
 */
export function useOnboarding() {
  const context = useContext(OnboardingContext);

  if (!context) {
    throw new Error(
      "useOnboarding debe utilizarse dentro de OnboardingProvider"
    );
  }

  return context;
}