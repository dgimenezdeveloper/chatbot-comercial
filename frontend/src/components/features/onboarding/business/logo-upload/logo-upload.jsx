"use client";

import Image from "next/image";
import { useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button/button";
import StoreIcon from "@/components/icons/dashboard/store";

const MAX_FILE_SIZE = 2 * 1024 * 1024;

const ALLOWED_IMAGE_TYPES = [
  "image/jpeg",
  "image/png",
];

export default function LogoUpload({
  value,
  error,
  onChange,
}) {
  const inputRef = useRef(null);
  const [localError, setLocalError] = useState("");

  // Derivación sincrónica con useMemo: elimina la necesidad de useState y evita llamar a setState en un efecto
  const previewUrl = useMemo(() => {
    if (!value) return null;
    if (typeof value === "string") return value;
    if (value instanceof Blob) return URL.createObjectURL(value);
    return null;
  }, [value]);

  // Limpieza de memoria del blob URL cuando el componente se desmonta o cambia de archivo
  useEffect(() => {
    return () => {
      if (previewUrl && typeof previewUrl === "string" && previewUrl.startsWith("blob:")) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleOpenFilePicker = () => {
    inputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setLocalError("");

    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setLocalError("Seleccioná una imagen JPG o PNG.");
      event.target.value = "";
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setLocalError("La imagen no puede superar los 2 MB.");
      event.target.value = "";
      return;
    }

    onChange(file);

    event.target.value = "";
  };

  const displayedError = localError || error;

  return (
    <div className="w-full max-w-30">
      <p className="mb-3 text-sm font-medium text-slate-950">
        Foto de perfil
      </p>

      <div
        className="
          relative
          aspect-square
          w-full
          overflow-hidden
          rounded-lg
          border
          border-slate-200
          bg-slate-50
        "
      >
        {previewUrl ? (
          <Image
            src={previewUrl}
            alt="Vista previa del logo del negocio"
            fill
            unoptimized
            sizes="120px"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center p-5">
            <StoreIcon className="w-full" />
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        className="sr-only"
        onChange={handleFileChange}
      />

      <Button
        type="button"
        variant="outline"
        onClick={handleOpenFilePicker}
        className="mt-4 w-full border-blue-500 text-blue-600 hover:bg-blue-50 hover:text-blue-700"
      >
        {value ? "Cambiar imagen" : "Subir imagen"}
      </Button>

      <p className="mt-2 text-center text-xs text-slate-400">
        JPG o PNG. Máx. 2 MB
      </p>

      {displayedError && (
        <p
          role="alert"
          className="mt-2 text-xs text-red-600"
        >
          {displayedError}
        </p>
      )}
    </div>
  );
}