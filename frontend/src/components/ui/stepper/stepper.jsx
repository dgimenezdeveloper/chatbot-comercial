/**
 * Componente reutilizable para mostrar una lista vertical de pasos.
 */
export default function Stepper({ steps, currentStep }) {
  return (
    <nav aria-label="Progreso del onboarding">
      <ol>
        {steps.map((step, index) => {
          const isActive = currentStep === step.number;
          const isCompleted = currentStep > step.number;

          return (
            <li
              key={step.number}
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
                    shrink-0
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
                  {step.number}
                </div>

                {index < steps.length - 1 && (
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
                  {step.label}
                </span>
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}