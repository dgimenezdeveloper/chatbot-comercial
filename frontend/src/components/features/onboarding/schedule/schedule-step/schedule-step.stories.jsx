import { useState } from "react";

import ScheduleStep from "@/components/features/onboarding/schedule/schedule-step/schedule-step";

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

const meta = {
  title: "Components/features/ScheduleStep",
  component: ScheduleStep,

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
};

export default meta;

function InteractiveScheduleStep() {
  const [data, setData] = useState(initialScheduleData);
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

  const handleContinue = () => {
    const newErrors = {};

    if (data.days.length === 0) {
      newErrors.days = "Seleccioná al menos un día de atención.";
    }

    if (!data.open) {
      newErrors.open = "Seleccioná un horario de apertura.";
    }

    if (!data.close) {
      newErrors.close = "Seleccioná un horario de cierre.";
    }

    if (data.open && data.close && data.open >= data.close) {
      newErrors.close =
        "El horario de cierre debe ser posterior al de apertura.";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      console.log("Horario válido:", data);
    }
  };

  return (
    <ScheduleStep
      data={data}
      errors={errors}
      onFieldChange={handleFieldChange}
      onBack={() => console.log("Volver")}
      onContinue={handleContinue}
    />
  );
}

export const Interactive = {
  render: () => <InteractiveScheduleStep />,
};

export const WithErrors = {
  args: {
    data: {
      days: [],
      open: "",
      close: "",
      lunchBreak: false,
    },
    errors: {
      days: "Seleccioná al menos un día de atención.",
      open: "Seleccioná un horario de apertura.",
      close: "Seleccioná un horario de cierre.",
    },
    onFieldChange: () => {},
    onBack: () => {},
    onContinue: () => {},
  },
};