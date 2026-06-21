import React, { useState, useEffect } from "react";
import { Checkbox } from "@/components/ui/checkbox/checkbox";
import { Label } from "@/components/ui/label/label";

export default {
  title: "Components/UI/Checkbox",
  component: Checkbox,
  parameters: {
    layout: "centered",
  },
  argTypes: {
    checked: {
      control: "boolean",
      description: "Estado actual del checkbox",
    },
    disabled: {
      control: "boolean",
      description: "Estado deshabilitado",
    },
  },
  args: {
    checked: false,
    disabled: false,
  },
};

export const Base = {
  render: (args) => {
    const [isChecked, setIsChecked] = useState(args.checked);

    return (
      <Checkbox
        {...args}
        checked={isChecked}
        onCheckedChange={setIsChecked}
        aria-label="Checkbox básico"
      />
    );
  },
};

export const WithLabel = {
  args: {
    labelText: "Aceptar términos y condiciones",
  },
  render: (args) => {
    const [isChecked, setIsChecked] = useState(args.checked);

    useEffect(() => {
      setIsChecked(args.checked);
    }, [args.checked]);

    return (
      <div className="flex items-center gap-2">
        <Checkbox
          id="terms-checkbox"
          checked={isChecked}
          onCheckedChange={setIsChecked}
          disabled={args.disabled}
        />
        <Label
          htmlFor="terms-checkbox"
          className={
            args.disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
          }
        >
          {args.labelText}
        </Label>
      </div>
    );
  },
};

export const Disabled = {
  args: {
    disabled: true,
    labelText: "Opción no disponible",
  },
  render: WithLabel.render,
};

export const WithVisualFeedback = {
  args: {
    labelText: "Activar notificaciones",
  },
  render: (args) => {
    const [isChecked, setIsChecked] = useState(args.checked);

    useEffect(() => {
      setIsChecked(args.checked);
    }, [args.checked]);

    return (
      <div className="flex flex-col gap-3 p-4 border rounded-md max-w-xs">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="notifications"
            checked={isChecked}
            onCheckedChange={setIsChecked}
            disabled={args.disabled}
          />
          <Label
            htmlFor="notifications"
            className={
              args.disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
            }
          >
            {args.labelText}
          </Label>
        </div>
        <p
          className={`text-sm ${isChecked ? "text-green-600" : "text-gray-500"}`}
        >
          {isChecked
            ? "¡Genial! Te enviaremos correos."
            : "No recibirás alertas."}
        </p>
      </div>
    );
  },
};
