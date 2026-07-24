import { cn } from "@/lib/utils";

/**
 * PageHeader — standardized header for all dashboard pages.
 *
 * Fixed-height design: the header always occupies the same vertical space
 * regardless of whether `subtitle` or `action` are provided.
 *
 * Layout:
 *   ┌─────────────────────────────────────────────┐  ← fixed h-14
 *   │ [icon]  TITLE           [optional action]   │
 *   └─────────────────────────────────────────────┘
 *      subtitle (positioned below, outside the fixed row)
 *   ──────────────────────────── separator ────────
 *
 * The icon and title are always vertically centered inside the fixed row.
 * The subtitle sits below the row and does NOT affect the row's height.
 * Adding/removing subtitle or action never shifts the separator position.
 *
 * Props:
 *   icon      — React node (lucide icon or custom SVG)
 *   title     — string, rendered uppercase
 *   subtitle  — optional string rendered below the fixed row
 *   action    — optional React node (Button) aligned to the right inside the row
 *   className — extra classes on the outer wrapper
 */
export function PageHeader({ icon, title, subtitle, action, className }) {
  return (
    <div className={cn("mb-6", className)}>

      {/* Fixed-height row — icon + title + optional action always same height */}
      <div className="flex h-14 items-center justify-between gap-4">

        {/* Left: icon badge + title */}
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              {icon}
            </div>
          )}
          <h1 className="text-xl font-bold tracking-wide text-foreground uppercase">
            {title}
          </h1>
        </div>

        {/* Right: optional action — takes up space even when absent to keep height stable */}
        <div className="shrink-0">
          {action ?? null}
        </div>
      </div>

      {/* Subtitle — lives outside the fixed row so it never shifts anything above */}
      {subtitle && (
        <p className="-mt-2 mb-1 text-sm text-muted-foreground">{subtitle}</p>
      )}

      {/* Separator — always at the same distance from the fixed row */}
      <hr className="border-border" />
    </div>
  );
}
