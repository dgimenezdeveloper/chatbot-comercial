"use client";

import { useRef, useState } from "react";
import { Store } from "lucide-react";
import { Button } from "@/components/ui/button/button";
import { cn } from "@/lib/utils";

/**
 * AvatarUpload — profile image picker with preview.
 *
 * Shows a placeholder (Store icon) or a preview of the selected image.
 * Accepts JPG/PNG up to 2MB (configurable).
 *
 * Props:
 *   value         — current image URL (controlled)
 *   onChange      — (file: File) => void called when user picks a file
 *   maxSizeMB     — max allowed size in MB (default: 2)
 *   accept        — MIME types string (default: "image/jpeg,image/png")
 *   label         — upload button label (default: "Subir imagen")
 *   hint          — hint text below button (default: "JPG o PNG. Máx. 2MB")
 *   className     — extra classes on the wrapper
 *
 * Usage:
 *   <AvatarUpload value={imageUrl} onChange={(file) => handleFileChange(file)} />
 */
export function AvatarUpload({
  value,
  onChange,
  maxSizeMB = 2,
  accept = "image/jpeg,image/png",
  label = "Subir imagen",
  hint,
  className,
}) {
  const inputRef = useRef(null);
  const [error, setError] = useState(null);

  const hintText = hint ?? `JPG o PNG. Máx. ${maxSizeMB}MB`;

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`El archivo supera los ${maxSizeMB}MB permitidos.`);
      return;
    }

    setError(null);
    onChange?.(file);
    // Reset input so the same file can be re-selected
    e.target.value = "";
  }

  return (
    <div className={cn("flex flex-col items-start gap-3", className)}>
      {/* Preview / placeholder */}
      <div
        className={cn(
          "flex size-32 items-center justify-center overflow-hidden rounded-xl border border-border bg-muted",
        )}
      >
        {value ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={value}
            alt="Vista previa"
            className="size-full object-cover"
          />
        ) : (
          <Store className="size-12 text-muted-foreground" />
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={handleFileChange}
        aria-label={label}
      />

      {/* Upload button */}
      <Button
        variant="outline"
        size="sm"
        type="button"
        onClick={() => inputRef.current?.click()}
      >
        {label}
      </Button>

      {/* Hint / error */}
      {error ? (
        <p className="text-xs text-destructive">{error}</p>
      ) : (
        <p className="text-xs text-muted-foreground">{hintText}</p>
      )}
    </div>
  );
}
