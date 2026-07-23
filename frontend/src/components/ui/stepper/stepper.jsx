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
            <li key={step.number} className="relative flex min-h-20 gap-4">
              <div className="flex flex-col items-center">
                <div
                  className={[
                    "z-10 flex size-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition",
                    isActive && "bg-primary text-primary-foreground",
                    isCompleted && "bg-accent text-primary",
                    !isActive && !isCompleted && "bg-secondary text-muted-foreground",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  {step.number}
                </div>

                {index < steps.length - 1 && (
                  <div
                    className={[
                      "h-full w-px",
                      isCompleted ? "bg-primary" : "bg-border",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  />
                )}
              </div>

              <div className="pt-2">
                <span
                  className={[
                    "text-sm font-medium",
                    isActive && "font-semibold text-primary",
                    isCompleted && "text-foreground",
                    !isActive && !isCompleted && "text-muted-foreground",
                  ]
                    .filter(Boolean)
                    .join(" ")}
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
