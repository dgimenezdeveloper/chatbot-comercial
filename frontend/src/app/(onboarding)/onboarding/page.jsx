"use client";

import { useState } from "react";
import { useOnboarding } from "@/components/features/onboarding/shared/onboarding-context/onboarding-context";

import BusinessStep from "@/components/features/onboarding/business/business-step/business-step";
import ScheduleStep from "@/components/features/onboarding/schedule/schedule-step/schedule-step";

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
  social: {
    whatsapp: "",
    instagram: "",
    facebook: "",
  },
};

/**
 * Datos iniciales del paso Horarios.
 *
 * Todos los días seleccionados comparten
 * el mismo horario de apertura y cierre.
 */
const initialScheduleData = {
  days: [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
  ],
  open: "09:00",
  close: "19:00",
  lunchBreak: false,
};

export default function OnboardingPage() {
  /**
   * Paso actual:
   *
   * 1 = Tu Negocio
   * 2 = Horarios
   */
  const { step, setStep } = useOnboarding();

  const [businessData, setBusinessData] = useState(
    initialBusinessData
  );

  const [scheduleData, setScheduleData] = useState(
    initialScheduleData
  );

  const [businessErrors, setBusinessErrors] = useState({});
  const [scheduleErrors, setScheduleErrors] = useState({});

  /**
   * Actualiza un campo principal del negocio.
   */
  const handleBusinessFieldChange = (field, value) => {
    setBusinessData((previousData) => ({
      ...previousData,
      [field]: value,
    }));

    setBusinessErrors((previousErrors) => ({
      ...previousErrors,
      [field]: "",
    }));
  };

  /**
   * Actualiza una red social.
   */
  const handleSocialChange = (field, value) => {
    setBusinessData((previousData) => ({
      ...previousData,
      social: {
        ...previousData.social,
        [field]: value,
      },
    }));
  };

  /**
   * Actualiza un campo del horario.
   *
   * Ejemplos:
   * handleScheduleFieldChange("open", "09:00")
   * handleScheduleFieldChange("days", ["monday"])
   */
  const handleScheduleFieldChange = (field, value) => {
    setScheduleData((previousData) => ({
      ...previousData,
      [field]: value,
    }));

    setScheduleErrors((previousErrors) => ({
      ...previousErrors,
      [field]: "",
      general: "",
    }));
  };

  /**
   * Validación del primer paso.
   */
  const validateBusinessStep = () => {
    const newErrors = {};

    if (!businessData.name.trim()) {
      newErrors.name = "El nombre es obligatorio.";
    }

    if (!businessData.description.trim()) {
      newErrors.description = "La descripción es obligatoria.";
    }

    if (!businessData.category) {
      newErrors.category = "Seleccioná una categoría.";
    }

    if (!businessData.address.trim()) {
      newErrors.address = "La dirección es obligatoria.";
    }

    if (!businessData.phone.trim()) {
      newErrors.phone = "El teléfono es obligatorio.";
    }

    if (!businessData.email.trim()) {
      newErrors.email = "El email es obligatorio.";
    } else {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!emailPattern.test(businessData.email)) {
        newErrors.email = "Ingresá un email válido.";
      }
    }

    setBusinessErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  /**
   * Validación del segundo paso.
   */
  const validateScheduleStep = () => {
    const newErrors = {};

    if (scheduleData.days.length === 0) {
      newErrors.days =
        "Seleccioná al menos un día de atención.";
    }

    if (!scheduleData.open) {
      newErrors.open =
        "Seleccioná un horario de apertura.";
    }

    if (!scheduleData.close) {
      newErrors.close =
        "Seleccioná un horario de cierre.";
    }

    /**
     * Como las horas tienen formato HH:mm,
     * pueden compararse directamente como texto.
     *
     * Ejemplo:
     * "09:00" es menor que "19:00".
     */
    if (
      scheduleData.open &&
      scheduleData.close &&
      scheduleData.open >= scheduleData.close
    ) {
      newErrors.close =
        "El horario de cierre debe ser posterior al de apertura.";
    }

    setScheduleErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  /**
   * Avanza desde Tu Negocio hacia Horarios.
   */
  const handleBusinessContinue = () => {
    const isValid = validateBusinessStep();

    if (!isValid) return;

    setStep(2);
  };

  /**
   * Regresa al primer paso.
   */
  const handleBack = () => {
    setStep(1);
  };

  /**
   * Finaliza el onboarding.
   */
  const handleScheduleContinue = () => {
    const isValid = validateScheduleStep();

    if (!isValid) return;

    const onboardingData = {
      business: businessData,
      schedule: scheduleData,
    };

    console.log("Onboarding completo:", onboardingData);

    // Aqui se pueden enviar los datos a un servidor o api para guardarlos.
  };

  return (
    <>
      {/* Paso 1 */}
      {step === 1 && (
        <BusinessStep
          data={businessData}
          errors={businessErrors}
          onFieldChange={handleBusinessFieldChange}
          onSocialChange={handleSocialChange}
          onContinue={handleBusinessContinue}
        />
      )}

      {/* Paso 2 */}
      {step === 2 && (
        <ScheduleStep
          data={scheduleData}
          errors={scheduleErrors}
          onFieldChange={handleScheduleFieldChange}
          onBack={handleBack}
          onContinue={handleScheduleContinue}
        />
      )}
    </>
  );
}