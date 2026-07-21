"use client";

import { Input } from "@/components/ui/input/input";
import { Label } from "@/components/ui/label/label";

import FieldError from "@/components/features/onboarding/shared/field-error/field-error";
/* import SocialMediaFields from "@/components/features/onboarding/business/social-media-field/social-media-field"; */

export default function ContactInfo({
  data,
  errors = {},
  onFieldChange,
}) {
  return (
    <div className="space-y-5">
      {/* Teléfono */}
      <div>
        <Label htmlFor="business-phone">
          Teléfono
        </Label>

        <Input
          id="business-phone"
          type="tel"
          value={data.phone}
          onChange={(event) =>
            onFieldChange("phone", event.target.value)
          }
          placeholder="Ej. 11 2233 4455"
          className="mt-2 h-11"
          aria-invalid={Boolean(errors.phone)}
        />

        <FieldError message={errors.phone} />
      </div>

      {/* Email */}
      <div>
        <Label htmlFor="business-email">
          Email de contacto
        </Label>

        <Input
          id="business-email"
          type="email"
          value={data.email}
          onChange={(event) =>
            onFieldChange("email", event.target.value)
          }
          placeholder="tu@mail.com"
          className="mt-2 h-11"
          aria-invalid={Boolean(errors.email)}
        />

        <FieldError message={errors.email} />
      </div>

      {/* Sitio web */}
      <div>
        <Label htmlFor="business-website">
          Sitio web{" "}
          <span className="font-normal text-slate-400">
            (opcional)
          </span>
        </Label>

        <Input
          id="business-website"
          type="url"
          value={data.website}
          onChange={(event) =>
            onFieldChange("website", event.target.value)
          }
          placeholder="Ej. www.tunegocio.com"
          className="mt-2 h-11"
        />
      </div>
    </div>
  );
}