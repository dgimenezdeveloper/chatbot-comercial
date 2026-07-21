"use client";

import { Input } from "@/components/ui/input/input";
import { Label } from "@/components/ui/label/label";





const SOCIAL_FIELDS = [
  {
    name: "instagram",
    label: "Instagram",
    placeholder: "Ej. @tunegocio",
    abbreviation: "IG",
  },
  {
    name: "facebook",
    label: "Facebook",
    placeholder: "Ej. /tunegocio",
    abbreviation: "f",
  },
  {
    name: "whatsapp",
    label: "WhatsApp",
    placeholder: "Ej. +54 11 2233 4455",
    abbreviation: "WA",
  },
];

export default function SocialMediaFields({
  data,
  onChange,
}) {
  return (
    <fieldset>
      <legend className="text-sm font-medium text-slate-950">
        Redes sociales{" "}
        <span className="font-normal text-slate-400">
          (opcional)
        </span>
      </legend>

      <div className="mt-3 space-y-3">
        {SOCIAL_FIELDS.map((social) => (
          <div
            key={social.name}
            className="flex items-center gap-3"
          >
            {/* Espacio temporal para el SVG de Figma */}
            <div
              className="
                flex
                h-11
                w-11
                shrink-0
                items-center
                justify-center
                rounded-md
                bg-slate-100
                text-xs
                font-semibold
                text-slate-700
              "
              aria-hidden="true"
            >
              {social.abbreviation}
            </div>

            <div className="flex-1">
              <Label
                htmlFor={`social-${social.name}`}
                className="sr-only"
              >
                {social.label}
              </Label>

              <Input
                id={`social-${social.name}`}
                value={data[social.name]}
                onChange={(event) =>
                  onChange(social.name, event.target.value)
                }
                placeholder={social.placeholder}
                className="h-11"
              />
            </div>
          </div>
        ))}
      </div>
    </fieldset>
  );
}