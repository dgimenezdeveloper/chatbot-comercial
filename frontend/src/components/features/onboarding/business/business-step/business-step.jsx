"use client";

import { Button } from "@/components/ui/button/button";

import BusinessInfo from "@/components/features/onboarding/business/business-info/business-info";
import ContactInfo from "@/components/features/onboarding/business/contact-info/contact-info";
import LogoUpload from "@/components/features/onboarding/business/logo-upload/logo-upload";
import SocialMediaFields from "@/components/features/onboarding/business/social-media-field/social-media-field";

export default function BusinessStep({
  data,
  errors = {},
  onFieldChange,
  onSocialChange,
  onContinue,
}) {
  return (
    <section className="flex flex-1 flex-col">
      {/* Encabezado */}
      <header className="border-b border-border pb-5">
        <h1 className="text-2xl font-bold text-foreground">Tu Negocio</h1>

        <p className="mt-2 text-sm text-muted-foreground">
          Contanos más sobre tu negocio. Esta información será visible
          para tus clientes.
        </p>
      </header>

      {/* Formulario */}
      <div className="flex-1 py-7">
        <div className="grid gap-8 xl:grid-cols-[120px_minmax(0,1fr)_minmax(300px,0.9fr)]">
          {/* Foto de perfil */}
          <LogoUpload
            value={data.logo}
            error={errors.logo}
            onChange={(file) =>
              onFieldChange("logo", file)
            }
          />

          {/* Información principal */}
          <BusinessInfo
            data={data}
            errors={errors}
            onFieldChange={onFieldChange}
          />

          {/* Contacto y redes */}
          <div className="border-border xl:border-l xl:pl-8">
            <div className="space-y-6">
              <ContactInfo
                data={data}
                errors={errors}
                onFieldChange={onFieldChange}
              />

              <SocialMediaFields
                data={data.social}
                onChange={onSocialChange}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Acciones */}
      <footer className="flex items-center justify-end border-t border-border pt-6">
        <Button type="button" onClick={onContinue} size="lg" className="min-w-64">
          Guardar y continuar
          <span aria-hidden="true">→</span>
        </Button>
      </footer>
    </section>
  );
}