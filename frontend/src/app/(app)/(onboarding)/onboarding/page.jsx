"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react"; // <-- IMPORT AGREGADO
import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";

import BusinessStep from "@/components/features/onboarding/business/business-step/business-step";
import ScheduleStep from "@/components/features/onboarding/schedule/schedule-step/schedule-step";

import { updateNegocio } from "@/services/negocio-api";
import {
  setBusinessData,
  markOnboardingCompleted,
  saveLogoFromFile,
} from "@/lib/business-store";

/**
 * Datos iniciales del paso Tu Negocio.
 */
const initialBusinessData = {
  logo: null,
  name: "",
  description: "",
  category: "",
  address: "",
  phone: "",
  email: "",
  website: "",
  social: {
    whatsapp: "",
    instagram: "",
    facebook: "",
  },
};

/**
 * Datos iniciales del paso Horarios.
 */
const initialScheduleData = {
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"],
  open: "09:00",
  close: "19:00",
  lunchBreak: false,
};

// ─── Validation helpers ──────────────────────────────────────────────────────

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_PATTERN = /^[\d\s+\-()]{7,20}$/;

function validateBusiness(data) {
  const errors = {};

  if (!data.name.trim()) {
    errors.name = "El nombre es obligatorio.";
  } else if (data.name.trim().length < 2) {
    errors.name = "El nombre debe tener al menos 2 caracteres.";
  }

  if (!data.description.trim()) {
    errors.description = "La descripción es obligatoria.";
  } else if (data.description.trim().length < 10) {
    errors.description = "La descripción debe tener al menos 10 caracteres.";
  }

  if (!data.category) {
    errors.category = "Seleccioná una categoría.";
  }

  if (!data.address.trim()) {
    errors.address = "La dirección es obligatoria.";
  } else if (data.address.trim().length < 5) {
    errors.address = "Ingresá una dirección más completa.";
  }

  if (!data.phone.trim()) {
    errors.phone = "El teléfono es obligatorio.";
  } else if (!PHONE_PATTERN.test(data.phone.trim())) {
    errors.phone = "Ingresá un teléfono válido (solo números, espacios, +, - y paréntesis).";
  }

  if (!data.email.trim()) {
    errors.email = "El email es obligatorio.";
  } else if (!EMAIL_PATTERN.test(data.email.trim())) {
    errors.email = "Ingresá un email válido (ej: tu@mail.com).";
  }

  return errors;
}

function validateSchedule(data) {
  const errors = {};

  if (data.days.length === 0) {
    errors.days = "Seleccioná al menos un día de atención.";
  }

  if (!data.open) {
    errors.open = "Seleccioná un horario de apertura.";
  }

  if (!data.close) {
    errors.close = "Seleccioná un horario de cierre.";
  }

  if (data.open && data.close && data.open >= data.close) {
    errors.close = "El horario de cierre debe ser posterior al de apertura.";
  }

  return errors;
}

// ─── Day labels for backend serialization ────────────────────────────────────

const DAY_LABELS = {
  monday: "Lunes",
  tuesday: "Martes",
  wednesday: "Miércoles",
  thursday: "Jueves",
  friday: "Viernes",
  saturday: "Sábado",
  sunday: "Domingo",
};

// ─── Page component ──────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const { step, setStep } = useOnboarding();
  const router = useRouter();
  const { update } = useSession(); // <-- HOOK AGREGADO

  const [businessData, setBusinessDataState] = useState(initialBusinessData);
  const [scheduleData, setScheduleData] = useState(initialScheduleData);
  const [businessErrors, setBusinessErrors] = useState({});
  const [scheduleErrors, setScheduleErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ─── Field change handlers ─────────────────────────────────────────────────

  const handleBusinessFieldChange = (field, value) => {
    setBusinessDataState((prev) => ({ ...prev, [field]: value }));
    setBusinessErrors((prev) => ({ ...prev, [field]: "" }));
  };

  const handleSocialChange = (field, value) => {
    setBusinessDataState((prev) => ({
      ...prev,
      social: { ...prev.social, [field]: value },
    }));
  };

  const handleScheduleFieldChange = (field, value) => {
    setScheduleData((prev) => ({ ...prev, [field]: value }));
    setScheduleErrors((prev) => ({ ...prev, [field]: "", general: "" }));
  };

  // ─── Step transitions ──────────────────────────────────────────────────────

  const handleBusinessContinue = () => {
    const errors = validateBusiness(businessData);
    setBusinessErrors(errors);
    if (Object.keys(errors).length > 0) return;
    setStep(2);
  };

  const handleBack = () => {
    setStep(1);
  };

  // ─── Final submission ──────────────────────────────────────────────────────

  const handleScheduleContinue = async () => {
    const errors = validateSchedule(scheduleData);
    setScheduleErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setIsSubmitting(true);

    try {
      // Build the horarios string for the backend
      const daysStr = scheduleData.days.map((d) => DAY_LABELS[d]).join(", ");
      const horariosStr = `${daysStr} de ${scheduleData.open} a ${scheduleData.close}`;

      // Build contacto string
      const contactParts = [businessData.email, businessData.phone];
      if (businessData.website) contactParts.push(businessData.website);
      const contactoStr = contactParts.join(" | ");

      // Call backend (demonstrates integration, backend echoes back)
      await updateNegocio({
        nombre: businessData.name.trim(),
        descripcion: businessData.description.trim(),
        categoria: businessData.category,
        horarios: horariosStr,
        contacto: contactoStr,
      });

      // Persist to localStorage
      const fullData = {
        name: businessData.name.trim(),
        description: businessData.description.trim(),
        category: businessData.category,
        address: businessData.address.trim(),
        phone: businessData.phone.trim(),
        email: businessData.email.trim(),
        website: businessData.website.trim(),
        social: businessData.social,
        schedule: scheduleData,
      };
      setBusinessData(fullData);

      // Save logo if uploaded
      if (businessData.logo) {
        await saveLogoFromFile(businessData.logo);
      }

      // Mark onboarding as completed
      markOnboardingCompleted();

      // <-- ACTUALIZACIÓN DE SESIÓN AGREGADA -->
      await update({ onboarding_completed: true });

      // Redirect to dashboard
      router.replace("/dashboard");
    } catch (error) {
      console.error("Error al guardar el negocio:", error);
      
      // Even if backend call fails, save locally for demo purposes
      const fullData = {
        name: businessData.name.trim(),
        description: businessData.description.trim(),
        category: businessData.category,
        address: businessData.address.trim(),
        phone: businessData.phone.trim(),
        email: businessData.email.trim(),
        website: businessData.website.trim(),
        social: businessData.social,
        schedule: scheduleData,
      };
      setBusinessData(fullData);

      if (businessData.logo) {
        await saveLogoFromFile(businessData.logo).catch(() => {});
      }

      markOnboardingCompleted();

      // <-- ACTUALIZACIÓN DE SESIÓN AGREGADA -->
      await update({ onboarding_completed: true });

      router.replace("/dashboard");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {step === 1 && (
        <BusinessStep
          data={businessData}
          errors={businessErrors}
          onFieldChange={handleBusinessFieldChange}
          onSocialChange={handleSocialChange}
          onContinue={handleBusinessContinue}
        />
      )}

      {step === 2 && (
        <ScheduleStep
          data={scheduleData}
          errors={scheduleErrors}
          onFieldChange={handleScheduleFieldChange}
          onBack={handleBack}
          onContinue={handleScheduleContinue}
          isSubmitting={isSubmitting}
        />
      )}
    </>
  );
}