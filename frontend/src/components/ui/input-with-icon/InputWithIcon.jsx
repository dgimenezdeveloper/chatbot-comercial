import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input/input";

/**
 * InputWithIcon — wraps the base Input with a leading icon slot.
 *
 * Props:
 *   icon      — React node rendered as the left prefix icon
 *   className — extra classes forwarded to the outer wrapper
 *   All other props are forwarded to the base Input
 *
 * Usage:
 *   <InputWithIcon icon={<Phone className="size-4" />} placeholder="Ej. 11 2233 4455" />
 */
export function InputWithIcon({ icon, className, ...props }) {
  return (
    <div className={cn("relative flex items-center", className)}>
      {icon && (
        <span className="pointer-events-none absolute left-3 flex items-center text-muted-foreground">
          {icon}
        </span>
      )}
      <Input
        className={cn(
          // Extra left padding when icon is present
          icon && "pl-9",
        )}
        {...props}
      />
    </div>
  );
}
