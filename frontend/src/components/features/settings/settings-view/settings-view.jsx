"use client";

import { useEffect, useState } from "react";
import { Bell, Building2, Calendar, CreditCard, Globe, Settings, Smartphone } from "lucide-react";

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
import { Textarea } from "@/components/ui/textarea/textarea";
import { cn } from "@/lib/utils";
import { fetchNegocio, updateNegocio } from "@/services/negocio-api";

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
    <section className="flex flex-col gap-5 rounded-xl border border-border bg-card p-6">
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
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function FieldRow({ label, htmlFor, hint, children }) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

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
      />
    </div>
  );
}

export default function SettingsView() {
  const [business, setBusiness] = useState({
    name: "",
    description: "",
    address: "",
    phone: "",
    email: "",
    website: "",
    instagram: "",
    facebook: "",
  });

  const [settings, setSettings] = useState({
    timezone: "America/Argentina/Buenos_Aires",
    currency: "ARS",
    ownerPhone: "",
    googleCalendarId: "",
    useWhatsappTemplates: false,
    smsEnabled: false,
    emailEnabled: false,
    acceptCards: true,
    acceptsCash: true,
    autoConfirm: true,
    enableServices: true,
    enableProducts: true,
    enableFaqs: true,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    let isMounted = true;
    async function loadBackendData() {
      try {
        const data = await fetchNegocio();
        if (isMounted && data) {
          setBusiness({
            name: data.nombre || "",
            description: data.descripcion || "",
            address: data.direccion || "",
            phone: data.telefono || "",
            email: data.email || "",
            website: data.website || "",
            instagram: data.instagram || "",
            facebook: data.facebook || "",
          });
          setSettings((prev) => ({
            ...prev,
            ownerPhone: data.owner_phone || "",
            googleCalendarId: data.google_calendar_id || "",
            enableServices: data.enable_services ?? true,
            enableProducts: data.enable_products ?? true,
            enableFaqs: data.enable_faqs ?? true,
          }));
        }
      } catch (err) {
        console.error("Error al cargar configuración desde backend:", err);
      }
    }
    loadBackendData();
    return () => {
      isMounted = false;
    };
  }, []);

  const updateBusiness = (field) => (e) =>
    setBusiness((prev) => ({ ...prev, [field]: e.target.value }));

  const updateSettings = (field) => (value) =>
    setSettings((prev) => ({ ...prev, [field]: value }));

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage("");

    try {
      const res = await updateNegocio({
        nombre: business.name.trim(),
        descripcion: business.description.trim(),
        direccion: business.address.trim(),
        telefono: business.phone.trim(),
        email: business.email.trim(),
        website: business.website.trim(),
        instagram: business.instagram.trim(),
        facebook: business.facebook.trim(),
        google_calendar_id: settings.googleCalendarId.trim(),
        horarios: "Lunes a Sábados de 09:00 a 20:00",
        contacto: [business.email, business.phone].filter(Boolean).join(" | "),
        owner_phone: settings.ownerPhone.trim(),
        enable_services: settings.enableServices,
        enable_products: settings.enableProducts,
        enable_faqs: settings.enableFaqs,
      });

      if (res) {
        setBusiness((prev) => ({
          ...prev,
          name: res.nombre || prev.name,
          description: res.descripcion || prev.description,
          address: res.direccion || prev.address,
          phone: res.telefono || prev.phone,
          email: res.email || prev.email,
          website: res.website || prev.website,
          instagram: res.instagram || prev.instagram,
          facebook: res.facebook || prev.facebook,
        }));
        setSettings((prev) => ({
          ...prev,
          ownerPhone: res.owner_phone || prev.ownerPhone,
          googleCalendarId: res.google_calendar_id || prev.googleCalendarId,
          enableServices: res.enable_services ?? prev.enableServices,
          enableProducts: res.enable_products ?? prev.enableProducts,
          enableFaqs: res.enable_faqs ?? prev.enableFaqs,
        }));
      }

      setSaveMessage("Cambios guardados correctamente en la base de datos.");
    } catch {
      setSaveMessage("Error al guardar en el servidor.");
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(""), 4000);
    }
  };

  return (
    <div className="flex flex-1 flex-col">
      <PageHeader
        icon={<Settings className="size-5" />}
        title="Configuración"
      />

      <div className="grid flex-1 gap-6 xl:grid-cols-2">
        {/* ── Mi Negocio ───────────────────────────────────────────────────── */}
        <SettingsSection
          icon={Building2}
          title="Mi Negocio"
          description="Información principal visible para tus clientes."
        >
          <FieldRow label="Nombre del negocio" htmlFor="biz-name">
            <Input
              id="biz-name"
              value={business.name}
              onChange={updateBusiness("name")}
              placeholder="Ej. Salón Pyme"
              className="h-10"
            />
          </FieldRow>

          <FieldRow label="Descripción" htmlFor="biz-description">
            <Textarea
              id="biz-description"
              value={business.description}
              onChange={updateBusiness("description")}
              placeholder="Contanos brevemente sobre tu negocio..."
              className="min-h-24 resize-none"
            />
          </FieldRow>

          <FieldRow label="Dirección" htmlFor="biz-address">
            <Input
              id="biz-address"
              value={business.address}
              onChange={updateBusiness("address")}
              placeholder="Ej. Av. Corrientes 1234, CABA"
              className="h-10"
            />
          </FieldRow>

          <FieldRow label="Teléfono comercial" htmlFor="biz-phone">
            <Input
              id="biz-phone"
              type="tel"
              value={business.phone}
              onChange={updateBusiness("phone")}
              placeholder="Ej. 11 2233 4455"
              className="h-10"
            />
          </FieldRow>

          <FieldRow label="Email comercial" htmlFor="biz-email">
            <Input
              id="biz-email"
              type="email"
              value={business.email}
              onChange={updateBusiness("email")}
              placeholder="tu@mail.com"
              className="h-10"
            />
          </FieldRow>

          <FieldRow label="Sitio web" htmlFor="biz-website">
            <Input
              id="biz-website"
              type="url"
              value={business.website}
              onChange={updateBusiness("website")}
              placeholder="https://www.tunegocio.com"
              className="h-10"
            />
          </FieldRow>
        </SettingsSection>

        {/* ── Módulos del Chatbot ──────────────────────────────────────────── */}
        <SettingsSection
          icon={Smartphone}
          title="Módulos del Chatbot"
          description="Elige qué secciones estarán visibles en el menú de WhatsApp para tus clientes."
        >
          <SwitchRow
            id="enable-services"
            label="Módulo de Turnos y Citas"
            description="Permite a tus clientes consultar disponibilidad y agendar turnos automáticamente."
            checked={settings.enableServices}
            onCheckedChange={updateSettings("enableServices")}
          />

          <SwitchRow
            id="enable-products"
            label="Módulo de Catálogo de Productos"
            description="Muestra tus productos en venta con precios y fotos."
            checked={settings.enableProducts}
            onCheckedChange={updateSettings("enableProducts")}
          />

          <SwitchRow
            id="enable-faqs"
            label="Preguntas Frecuentes e Información"
            description="Muestra información del local (horarios, ubicación, medios de pago)."
            checked={settings.enableFaqs}
            onCheckedChange={updateSettings("enableFaqs")}
          />
        </SettingsSection>

        {/* ── Integración Google Calendar ──────────────────────────────────── */}
        <SettingsSection
          icon={Calendar}
          title="Google Calendar"
          description="Sincronización bidireccional de citas."
        >
          <FieldRow
            label="ID de Calendario Dedicado"
            htmlFor="gcal-id"
            hint="Ingresa el ID del calendario secundario de Google para este negocio (ej: c_12345@group.calendar.google.com o 'primary')."
          >
            <Input
              id="gcal-id"
              placeholder="primary"
              value={settings.googleCalendarId}
              onChange={(e) => updateSettings("googleCalendarId")(e.target.value)}
              className="h-10 font-mono text-xs"
            />
          </FieldRow>
        </SettingsSection>

        {/* ── Recordatorios ────────────────────────────────────────────────── */}
        <SettingsSection
          icon={Bell}
          title="Recordatorios & Handover"
          description="Canales de notificación para turnos y atención humana."
        >
          <FieldRow
            label="WhatsApp del dueño / Administrador"
            htmlFor="owner-phone"
            hint="Número en formato E.164 (+54911...) que recibirá notificaciones y respuestas del chatbot para atención manual."
          >
            <Input
              id="owner-phone"
              type="tel"
              placeholder="+5491112345678"
              value={settings.ownerPhone}
              onChange={(e) => updateSettings("ownerPhone")(e.target.value)}
              className="h-10"
            />
          </FieldRow>

          <SwitchRow
            id="whatsapp-templates"
            label="Templates de WhatsApp"
            description="Usa plantillas oficiales de Meta para recordatorios fuera de la ventana de 24 h."
            checked={settings.useWhatsappTemplates}
            onCheckedChange={updateSettings("useWhatsappTemplates")}
          />
        </SettingsSection>

        {/* ── Regional ─────────────────────────────────────────────────────── */}
        <SettingsSection
          icon={Globe}
          title="Regional"
          description="Zona horaria y moneda para turnos y precios."
        >
          <FieldRow label="Zona horaria" htmlFor="timezone">
            <Select
              value={settings.timezone}
              onValueChange={updateSettings("timezone")}
              items={TIMEZONES}
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
              onValueChange={updateSettings("currency")}
              items={CURRENCIES}
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
      </div>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <div className="mt-6 flex items-center justify-between border-t border-border pt-6">
        {saveMessage && (
          <p className="text-sm font-medium text-primary">{saveMessage}</p>
        )}
        {!saveMessage && <div />}
        <Button type="button" size="lg" onClick={handleSave} disabled={isSaving}>
          {isSaving ? "Guardando..." : "Guardar cambios"}
        </Button>
      </div>
    </div>
  );
}