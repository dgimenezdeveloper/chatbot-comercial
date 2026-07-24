"use client";

import { MapPin, Store } from "lucide-react";

import { InputWithIcon } from "@/components/ui/input-with-icon/InputWithIcon";
import { Label } from "@/components/ui/label/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select/select";
import { Textarea } from "@/components/ui/textarea/textarea";
import FieldError from "@/components/features/onboarding/shared/field-error/field-error";

export default function BusinessInfo({ data, errors = {}, onFieldChange }) {
  return (
    <div className="space-y-6">
      {/* Nombre */}
      <div>
        <Label htmlFor="business-name">Nombre del Negocio</Label>
        <InputWithIcon
          id="business-name"
          icon={<Store className="size-4" />}
          value={data.name}
          onChange={(e) => onFieldChange("name", e.target.value)}
          placeholder="Ej. Salón Marilyn"
          className="mt-2 h-11"
          aria-invalid={Boolean(errors.name)}
        />
        <FieldError message={errors.name} />
      </div>

      {/* Descripción */}
      <div>
        <Label htmlFor="business-description">Descripción del Negocio</Label>
        <Textarea
          id="business-description"
          value={data.description}
          onChange={(e) => onFieldChange("description", e.target.value)}
          placeholder="Contanos brevemente sobre tu negocio, tus servicios y lo que te diferencia..."
          className="mt-2 min-h-40 resize-none"
          aria-invalid={Boolean(errors.description)}
        />
        <FieldError message={errors.description} />
      </div>

      {/* Categoría */}
      <div>
        <Label htmlFor="business-category">Categoría</Label>
        <Select
          value={data.category}
          onValueChange={(value) => onFieldChange("category", value)}
        >
          <SelectTrigger
            id="business-category"
            className="mt-2 h-11 w-full"
            aria-invalid={Boolean(errors.category)}
          >
            <SelectValue placeholder="Seleccioná la categoría de tu negocio" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="hair-salon">Peluquería</SelectItem>
            <SelectItem value="barbershop">Barbería</SelectItem>
            <SelectItem value="beauty-center">Centro de estética</SelectItem>
            <SelectItem value="nail-salon">Salón de uñas</SelectItem>
            <SelectItem value="spa">Spa</SelectItem>
          </SelectContent>
        </Select>
        <FieldError message={errors.category} />
      </div>

      {/* Dirección */}
      <div>
        <Label htmlFor="business-address">Dirección</Label>
        <InputWithIcon
          id="business-address"
          icon={<MapPin className="size-4" />}
          value={data.address}
          onChange={(e) => onFieldChange("address", e.target.value)}
          placeholder="Ej. Av. Corrientes 1234, CABA"
          className="mt-2 h-11"
          aria-invalid={Boolean(errors.address)}
        />
        <FieldError message={errors.address} />
      </div>
    </div>
  );
}
