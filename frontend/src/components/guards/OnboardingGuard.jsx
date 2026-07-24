"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Loader2 } from "lucide-react";
import { isOnboardingCompleted } from "@/lib/business-store";

/**
 * OnboardingGuard — Client-side route guard.
 *
 * Behavior:
 *   - On dashboard routes: if onboarding is NOT completed → redirect to /onboarding
 *   - On onboarding route: if onboarding IS completed → redirect to /dashboard
 *
 * This guard wraps the layout children and shows a loading spinner
 * during the check to prevent content flash.
 *
 * Props:
 *   requireOnboarding — if true, redirects to /onboarding when flag is missing (use on dashboard)
 *   requireCompleted  — if true, redirects to /dashboard when flag IS set (use on onboarding)
 */
export function OnboardingGuard({ requireOnboarding = false, requireCompleted = false, children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const completed = isOnboardingCompleted();

    if (requireOnboarding && !completed) {
      router.replace("/onboarding");
      return;
    }

    if (requireCompleted && completed) {
      router.replace("/dashboard");
      return;
    }

    setChecked(true);
  }, [requireOnboarding, requireCompleted, router, pathname]);

  if (!checked) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="size-8 animate-spin text-primary" />
      </div>
    );
  }

  return children;
}
