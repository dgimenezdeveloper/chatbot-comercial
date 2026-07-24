import { ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button/button";
import { cn } from "@/lib/utils";

/**
 * FormFooter — standardized footer for multi-step forms (onboarding, wizards).
 *
 * Renders two buttons left-aligned (Volver) and right-aligned (Guardar y continuar),
 * matching the wireframe layout. A top border separates it from the form content.
 *
 * Props:
 *   onBack          — handler for the back button. If omitted, back button is hidden.
 *   onNext          — handler for the next/submit button.
 *   backLabel       — label for back button (default: "Volver")
 *   nextLabel       — label for next button (default: "Guardar y continuar")
 *   isLoading       — shows a loading state on the next button
 *   nextDisabled    — disables the next button
 *   className       — extra classes on the wrapper
 *
 * Usage:
 *   <FormFooter onBack={handleBack} onNext={handleSubmit} />
 */
export function FormFooter({
  onBack,
  onNext,
  backLabel = "Volver",
  nextLabel = "Guardar y continuar",
  isLoading = false,
  nextDisabled = false,
  className,
}) {
  return (
    <div
      className={cn(
        "mt-auto flex items-center justify-between border-t border-border pt-6",
        className,
      )}
    >
      {/* Back */}
      {onBack ? (
        <Button variant="outline" size="lg" onClick={onBack} type="button">
          <ArrowLeft className="size-4" />
          {backLabel}
        </Button>
      ) : (
        // Empty spacer so the next button always stays right-aligned
        <span />
      )}

      {/* Next / Submit */}
      <Button
        size="lg"
        onClick={onNext}
        disabled={isLoading || nextDisabled}
        type={onNext ? "button" : "submit"}
        className="min-w-48"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="size-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
            Guardando...
          </span>
        ) : (
          <>
            {nextLabel}
            <ArrowRight className="size-4" />
          </>
        )}
      </Button>
    </div>
  );
}
