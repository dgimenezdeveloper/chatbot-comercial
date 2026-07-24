"use client";

import { cn } from "@/lib/utils";
import LogoPymio from "@/components/icons/logo-pymio";

/**
 * MobileStepIndicator — sticky top bar for onboarding on mobile.
 *
 * Shows the Pymio logo + a row of colored pills (one per step).
 * Each pill fills with bg-primary when that step is reached.
 * Sticks to the top so the user always sees their progress while scrolling.
 *
 * Props:
 *   currentStep — 1-indexed current step
 *   steps       — array of { number, label }
 *   className   — extra classes
 */
export function MobileStepIndicator({ currentStep, steps, className }) {
  return (
    <div
      className={cn(
        "sticky top-0 z-30 lg:hidden",
        "flex flex-col gap-3",
        "bg-card border-b border-border px-4 py-3",
        className,
      )}
    >
      {/* Logo */}
      <div className="flex justify-center">
        <LogoPymio className="h-8 w-[62px]" aria-label="PYMIO" />
      </div>

      {/* Step pills */}
      <div className="flex items-center gap-2">
        {steps.map((s) => {
          const isCompleted = s.number < currentStep;
          const isActive = s.number === currentStep;

          return (
            <div key={s.number} className="flex flex-1 flex-col items-center gap-1">
              {/* Pill / progress line */}
              <div
                className={cn(
                  "h-1.5 w-full rounded-full transition-colors duration-300",
                  isCompleted || isActive ? "bg-primary" : "bg-muted",
                )}
                role="presentation"
              />
              {/* Step label */}
              <span
                className={cn(
                  "text-[10px] font-medium transition-colors duration-300",
                  isActive ? "text-primary" : isCompleted ? "text-primary/70" : "text-muted-foreground",
                )}
              >
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
