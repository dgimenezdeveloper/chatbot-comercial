"use client";

import { Globe, Mail, Phone } from "lucide-react";

import { InputWithIcon } from "@/components/ui/input-with-icon/InputWithIcon";
import { Label } from "@/components/ui/label/label";
import FieldError from "@/components/features/onboarding/shared/field-error/field-error";

export default function ContactInfo({ data, errors = {}, onFieldChange }) {
  return (
    <div className="space-y-5">
      {/* Teléfono */}
      <div>
        <Label htmlFor="business-phone">Teléfono</Label>
        <InputWithIcon
          id="business-phone"
          type="tel"
          icon={<Phone className="size-4" />}
          value={data.phone}
          onChange={(e) => onFieldChange("phone", e.target.value)}
          placeholder="Ej. 11 2233 4455"
          className="mt-2 h-11"
          aria-invalid={Boolean(errors.phone)}
        />
        <FieldError message={errors.phone} />
      </div>

      {/* Email */}
      <div>
        <Label htmlFor="business-email">Email de contacto</Label>
        <InputWithIcon
          id="business-email"
          type="email"
          icon={<Mail className="size-4" />}
          value={data.email}
          onChange={(e) => onFieldChange("email", e.target.value)}
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
          <span className="font-normal text-muted-foreground">(opcional)</span>
        </Label>
        <InputWithIcon
          id="business-website"
          type="url"
          icon={<Globe className="size-4" />}
          value={data.website}
          onChange={(e) => onFieldChange("website", e.target.value)}
          placeholder="Ej. www.tunegocio.com"
          className="mt-2 h-11"
        />
      </div>
    </div>
  );
}
