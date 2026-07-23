"use client";

import { useState } from "react";
import { Bell, CreditCard, Globe, Smartphone } from "lucide-react";

import { Button } from "@/components/ui/button/button";
import { Checkbox } from "@/components/ui/checkbox/checkbox";
import { Input } from "@/components/ui/input/input";
import { Label } from "@/components/ui/label/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select/select";

const TIMEZONES = [
  { value: "America/Argentina/Buenos_Aires", label: "Buenos Aires (GMT-3)" },
  { value: "America/Argentina/Cordoba", label: "Córdoba (GMT-3)" },
  { value: "America/Santiago", label: "Santiago (GMT-4)" },
  { value: "America/Mexico_City", label: "Ciudad de México (GMT-6)" },
];

const CURRENCIES = [
  { value: "ARS", label: "Peso argentino (ARS)" },
  { value: "USD", label: "Dólar estadounidense (USD)" },
  { value: "CLP", label: "Peso chileno (CLP)" },
  { value: "MXN", label: "Peso mexicano (MXN)" },
];

function SettingsSection({ icon: Icon, title, description, children }) {
  return (
    <section className="rounded-xl border border-border bg-background p-6">
      <div className="mb-5 flex items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-accent text-primary">
          <Icon className="size-5" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          {description && (
            <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function ToggleRow({ id, label, description, checked, onCheckedChange }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-border px-4 py-3">
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={(value) => onCheckedChange(value === true)}
      />
      <div>
        <Label htmlFor={id} className="cursor-pointer font-medium text-foreground">
          {label}
        </Label>
        {description && (
          <p className="mt-1 text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
}

export default function SettingsView() {
  const [settings, setSettings] = useState({
    timezone: "America/Argentina/Buenos_Aires",
    currency: "ARS",
    ownerPhone: "",
    useWhatsappTemplates: false,
    smsEnabled: false,
    emailEnabled: false,
    acceptCards: true,
    acceptsCash: true,
  });

  const updateSetting = (field, value) => {
    setSettings((previous) => ({ ...previous, [field]: value }));
  };

  const handleSave = () => {
    console.log("Configuración guardada:", settings);
  };

  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <h1 className="text-2xl font-bold text-foreground">Configuración</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Administrá las preferencias generales de tu negocio y del chatbot.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-2">
        <SettingsSection
          icon={Globe}
          title="Regional"
          description="Zona horaria y moneda para turnos y precios."
        >
          <div>
            <Label htmlFor="timezone">Zona horaria</Label>
            <Select
              value={settings.timezone}
              onValueChange={(value) => updateSetting("timezone", value)}
            >
              <SelectTrigger id="timezone" className="mt-2 h-11 w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONES.map((timezone) => (
                  <SelectItem key={timezone.value} value={timezone.value}>
                    {timezone.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="currency">Moneda</Label>
            <Select
              value={settings.currency}
              onValueChange={(value) => updateSetting("currency", value)}
            >
              <SelectTrigger id="currency" className="mt-2 h-11 w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CURRENCIES.map((currency) => (
                  <SelectItem key={currency.value} value={currency.value}>
                    {currency.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </SettingsSection>

        <SettingsSection
          icon={Bell}
          title="Recordatorios"
          description="Canales de notificación para turnos y alertas."
        >
          <div>
            <Label htmlFor="owner-phone">WhatsApp del dueño</Label>
            <Input
              id="owner-phone"
              type="tel"
              placeholder="+54 9 11 1234-5678"
              value={settings.ownerPhone}
              onChange={(event) => updateSetting("ownerPhone", event.target.value)}
              className="mt-2 h-11"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Recibís alertas cuando falle un recordatorio automático.
            </p>
          </div>

          <ToggleRow
            id="whatsapp-templates"
            label="Templates de WhatsApp"
            description="Usa plantillas oficiales de Meta para recordatorios fuera de la ventana de 24 h."
            checked={settings.useWhatsappTemplates}
            onCheckedChange={(value) => updateSetting("useWhatsappTemplates", value)}
          />

          <ToggleRow
            id="sms-enabled"
            label="SMS como canal alternativo"
            description="Envía recordatorios por SMS si WhatsApp no está disponible."
            checked={settings.smsEnabled}
            onCheckedChange={(value) => updateSetting("smsEnabled", value)}
          />

          <ToggleRow
            id="email-enabled"
            label="Email como canal alternativo"
            description="Envía confirmaciones y recordatorios por correo electrónico."
            checked={settings.emailEnabled}
            onCheckedChange={(value) => updateSetting("emailEnabled", value)}
          />
        </SettingsSection>

        <SettingsSection
          icon={CreditCard}
          title="Métodos de pago"
          description="Opciones que el chatbot puede informar a tus clientes."
        >
          <ToggleRow
            id="accept-cards"
            label="Tarjetas de crédito y débito"
            checked={settings.acceptCards}
            onCheckedChange={(value) => updateSetting("acceptCards", value)}
          />

          <ToggleRow
            id="accepts-cash"
            label="Efectivo"
            checked={settings.acceptsCash}
            onCheckedChange={(value) => updateSetting("acceptsCash", value)}
          />
        </SettingsSection>

        <SettingsSection
          icon={Smartphone}
          title="Chatbot"
          description="Preferencias de funcionamiento del asistente virtual."
        >
          <ToggleRow
            id="auto-confirm"
            label="Confirmación automática de turnos"
            description="Los turnos se confirman al crearse sin intervención manual."
            checked
            onCheckedChange={() => {}}
          />

          <p className="text-xs text-muted-foreground">
            Más opciones de personalización del chatbot estarán disponibles próximamente.
          </p>
        </SettingsSection>
      </div>

      <footer className="flex justify-end border-t border-border pt-6">
        <Button type="button" size="lg" onClick={handleSave}>
          Guardar cambios
        </Button>
      </footer>
    </div>
  );
}
