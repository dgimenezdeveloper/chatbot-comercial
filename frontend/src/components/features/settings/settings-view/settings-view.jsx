"use client";

import { useState } from "react";
import { Bell, CreditCard, Globe, Settings, Smartphone } from "lucide-react";

import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button/button";
import { Input } from "@/components/ui/input/input";
import { Label } from "@/components/ui/label/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select/select";
import { Switch } from "@/components/ui/switch/switch";
import { cn } from "@/lib/utils";

// ─── Data ────────────────────────────────────────────────────────────────────

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

// ─── Shared sub-components ───────────────────────────────────────────────────

/**
 * SettingsSection — card wrapper for a group of related settings.
 * Uses Card-like styling consistent with the rest of the app.
 */
function SettingsSection({ icon: Icon, title, description, children }) {
  return (
    <section className="flex flex-col gap-5 rounded-xl border border-border bg-card p-6">
      {/* Section header */}
      <div className="flex items-start gap-3">
        <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Icon className="size-4" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-foreground">{title}</h2>
          {description && (
            <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4">{children}</div>
    </section>
  );
}

/**
 * FieldRow — label + control stacked vertically.
 */
function FieldRow({ label, htmlFor, hint, children }) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

/**
 * SwitchRow — full-width row with label/description on the left, Switch on the right.
 * Consistent with the toggle patterns used across the dashboard.
 */
function SwitchRow({ id, label, description, checked, onCheckedChange, disabled }) {
  return (
    <div
      className={cn(
        "flex items-start justify-between gap-4 rounded-lg border border-border px-4 py-3",
        disabled && "opacity-60",
      )}
    >
      <div className="flex-1">
        <Label
          htmlFor={id}
          className={cn("cursor-pointer font-medium", disabled && "cursor-not-allowed")}
        >
          {label}
        </Label>
        {description && (
          <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
        aria-describedby={description ? `${id}-desc` : undefined}
      />
    </div>
  );
}

// ─── Main component ──────────────────────────────────────────────────────────

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
    autoConfirm: true,
  });

  const update = (field) => (value) =>
    setSettings((prev) => ({ ...prev, [field]: value }));

  const handleSave = () => {
    // TODO: connect to API
    console.log("Configuración guardada:", settings);
  };

  return (
    <div className="flex flex-1 flex-col">
      <PageHeader
        icon={<Settings className="size-5" />}
        title="Configuración"
      />

      <div className="grid flex-1 gap-6 xl:grid-cols-2">
        {/* ── Regional ─────────────────────────────────────────────────────── */}
        <SettingsSection
          icon={Globe}
          title="Regional"
          description="Zona horaria y moneda para turnos y precios."
        >
          <FieldRow label="Zona horaria" htmlFor="timezone">
            <Select
              value={settings.timezone}
              onValueChange={update("timezone")}
            >
              <SelectTrigger id="timezone" className="h-10 w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONES.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    {tz.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FieldRow>

          <FieldRow label="Moneda" htmlFor="currency">
            <Select
              value={settings.currency}
              onValueChange={update("currency")}
            >
              <SelectTrigger id="currency" className="h-10 w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CURRENCIES.map((c) => (
                  <SelectItem key={c.value} value={c.value}>
                    {c.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FieldRow>
        </SettingsSection>

        {/* ── Recordatorios ────────────────────────────────────────────────── */}
        <SettingsSection
          icon={Bell}
          title="Recordatorios"
          description="Canales de notificación para turnos y alertas."
        >
          <FieldRow
            label="WhatsApp del dueño"
            htmlFor="owner-phone"
            hint="Recibís alertas cuando falle un recordatorio automático."
          >
            <Input
              id="owner-phone"
              type="tel"
              placeholder="+54 9 11 1234-5678"
              value={settings.ownerPhone}
              onChange={(e) => update("ownerPhone")(e.target.value)}
              className="h-10"
            />
          </FieldRow>

          <SwitchRow
            id="whatsapp-templates"
            label="Templates de WhatsApp"
            description="Usa plantillas oficiales de Meta para recordatorios fuera de la ventana de 24 h."
            checked={settings.useWhatsappTemplates}
            onCheckedChange={update("useWhatsappTemplates")}
          />

          <SwitchRow
            id="sms-enabled"
            label="SMS como canal alternativo"
            description="Envía recordatorios por SMS si WhatsApp no está disponible."
            checked={settings.smsEnabled}
            onCheckedChange={update("smsEnabled")}
          />

          <SwitchRow
            id="email-enabled"
            label="Email como canal alternativo"
            description="Envía confirmaciones y recordatorios por correo electrónico."
            checked={settings.emailEnabled}
            onCheckedChange={update("emailEnabled")}
          />
        </SettingsSection>

        {/* ── Métodos de pago ───────────────────────────────────────────────── */}
        <SettingsSection
          icon={CreditCard}
          title="Métodos de pago"
          description="Opciones que el chatbot puede informar a tus clientes."
        >
          <SwitchRow
            id="accept-cards"
            label="Tarjetas de crédito y débito"
            checked={settings.acceptCards}
            onCheckedChange={update("acceptCards")}
          />

          <SwitchRow
            id="accepts-cash"
            label="Efectivo"
            checked={settings.acceptsCash}
            onCheckedChange={update("acceptsCash")}
          />
        </SettingsSection>

        {/* ── Chatbot ───────────────────────────────────────────────────────── */}
        <SettingsSection
          icon={Smartphone}
          title="Chatbot"
          description="Preferencias de funcionamiento del asistente virtual."
        >
          <SwitchRow
            id="auto-confirm"
            label="Confirmación automática de turnos"
            description="Los turnos se confirman al crearse sin intervención manual."
            checked={settings.autoConfirm}
            onCheckedChange={update("autoConfirm")}
          />

          <p className="text-xs text-muted-foreground">
            Más opciones de personalización del chatbot estarán disponibles próximamente.
          </p>
        </SettingsSection>
      </div>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <div className="mt-6 flex justify-end border-t border-border pt-6">
        <Button type="button" size="lg" onClick={handleSave}>
          Guardar cambios
        </Button>
      </div>
    </div>
  );
}
