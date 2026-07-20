import { useState } from "react";
import { fn } from "storybook/test";

import BusinessStep from "@/components/features/onboarding/business/business-step/business-step";

/**
 * Datos vacíos para las historias.
 */
const emptyBusinessData = {
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
 * Ejemplo de datos ya completados.
 */
const completedBusinessData = {
  logo: null,
  name: "Salón Marilyn",
  description:
    "Peluquería especializada en cortes, coloración y tratamientos capilares.",
  category: "peluqueria",
  address: "Av. Corrientes 1234, CABA",
  phone: "11 2233 4455",
  email: "contacto@salonmarilyn.com",
  social: {
    whatsapp: "11 2233 4455",
    instagram: "@salonmarilyn",
    facebook: "Salón Marilyn",
  },
};

const meta = {
  title: "Components/features/BusinessStep",
  component: BusinessStep,

  parameters: {
    layout: "fullscreen",
  },

  decorators: [
    (Story) => (
      <div className="min-h-screen bg-white p-6 sm:p-8 lg:p-12">
        <Story />
      </div>
    ),
  ],

  // Funciones simuladas para las historias no interactivas.
  args: {
    onFieldChange: fn(),
    onSocialChange: fn(),
    onContinue: fn(),
  },
};

export default meta;

/**
 * Formulario completamente vacío.
 */
export const Empty = {
  args: {
    data: emptyBusinessData,
    errors: {},
  },
};

/**
 * Formulario con datos de ejemplo.
 */
export const Completed = {
  args: {
    data: completedBusinessData,
    errors: {},
  },
};

/**
 * Permite visualizar los mensajes de validación.
 */
export const WithErrors = {
  args: {
    data: emptyBusinessData,
    errors: {
      name: "El nombre es obligatorio.",
      description: "La descripción es obligatoria.",
      category: "Seleccioná una categoría.",
      address: "La dirección es obligatoria.",
      phone: "El teléfono es obligatorio.",
      email: "El email es obligatorio.",
    },
  },
};

/**
 * Componente auxiliar que administra estado solamente
 * para demostrar el formulario dentro de Storybook.
 */
function InteractiveBusinessStep() {
  const [data, setData] = useState(emptyBusinessData);
  const [errors, setErrors] = useState({});

  const handleFieldChange = (field, value) => {
    setData((previousData) => ({
      ...previousData,
      [field]: value,
    }));

    setErrors((previousErrors) => ({
      ...previousErrors,
      [field]: "",
    }));
  };

  const handleSocialChange = (field, value) => {
    setData((previousData) => ({
      ...previousData,
      social: {
        ...previousData.social,
        [field]: value,
      },
    }));
  };

  const handleContinue = () => {
    const newErrors = {};

    if (!data.name.trim()) {
      newErrors.name = "El nombre es obligatorio.";
    }

    if (!data.description.trim()) {
      newErrors.description = "La descripción es obligatoria.";
    }

    if (!data.category) {
      newErrors.category = "Seleccioná una categoría.";
    }

    if (!data.address.trim()) {
      newErrors.address = "La dirección es obligatoria.";
    }

    if (!data.phone.trim()) {
      newErrors.phone = "El teléfono es obligatorio.";
    }

    if (!data.email.trim()) {
      newErrors.email = "El email es obligatorio.";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      console.log("Formulario válido en Storybook:", data);
    }
  };

  return (
    <BusinessStep
      data={data}
      errors={errors}
      onFieldChange={handleFieldChange}
      onSocialChange={handleSocialChange}
      onContinue={handleContinue}
    />
  );
}

/**
 * Historia completamente funcional.
 *
 * Permite escribir, seleccionar categoría, cargar un archivo
 * y probar la validación.
 */
export const Interactive = {
  render: () => <InteractiveBusinessStep />,
};