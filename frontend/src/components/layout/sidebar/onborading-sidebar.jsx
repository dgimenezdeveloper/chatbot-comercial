"use client";

import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";

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
  /**
   * Obtenemos el paso actual desde el Context.
   */
  const { step } = useOnboarding();

  return (
    <div className="flex min-h-screen flex-col border-r border-slate-200 bg-slate-50 px-8 py-10">
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

      {/* Lista de pasos */}
      <nav aria-label="Progreso del onboarding">
        <ol>
          {STEPS.map((sidebarStep, index) => {
            const isActive = step === sidebarStep.number;
            const isCompleted = step > sidebarStep.number;

            return (
              <li
                key={sidebarStep.number}
                className="relative flex min-h-24 gap-4"
              >
                {/* Círculo y línea vertical */}
                <div className="flex flex-col items-center">
                  <div
                    className={`
                      z-10
                      flex
                      h-9
                      w-9
                      items-center
                      justify-center
                      rounded-full
                      text-sm
                      font-semibold
                      transition
                      ${
                        isActive
                          ? "bg-blue-600 text-white"
                          : isCompleted
                            ? "bg-blue-100 text-blue-700"
                            : "bg-slate-200 text-slate-500"
                      }
                    `}
                  >
                    {sidebarStep.number}
                  </div>

                  {/* No mostramos la línea después del último paso */}
                  {index < STEPS.length - 1 && (
                    <div
                      className={`
                        h-full
                        w-px
                        ${
                          isCompleted
                            ? "bg-blue-500"
                            : "bg-slate-300"
                        }
                      `}
                    />
                  )}
                </div>

                {/* Nombre del paso */}
                <div className="pt-2">
                  <span
                    className={`
                      text-sm
                      font-medium
                      ${
                        isActive
                          ? "text-blue-700"
                          : isCompleted
                            ? "text-slate-700"
                            : "text-slate-500"
                      }
                    `}
                  >
                    {sidebarStep.label}
                  </span>
                </div>
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
}