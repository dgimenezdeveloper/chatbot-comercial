import React, { useState, useEffect } from "react";
import { Switch } from "@/components/ui/switch/switch";
import { Label } from "@/components/ui/label/label";

export default {
  title: "Components/UI/Switch",
  component: Switch,
  parameters: {
    layout: "centered",
  },
  argTypes: {
    checked: {
      control: "boolean",
      description: "Estado actual del Switch",
    },
    disabled: {
      control: "boolean",
      description: "Estado deshabilitado",
    },
    size: {
      control: "select",
      options: ["sm", "default"],
      description: "Tamaño visual del Switch",
    },
  },
  args: {
    checked: false,
    disabled: false,
    size: "default",
  },
};

export const Base = {
  render: (args) => {
    const [isChecked, setIsChecked] = useState(args.checked);

    useEffect(() => {
      setIsChecked(args.checked);
    }, [args.checked]);

    return (
      <Switch {...args} checked={isChecked} onCheckedChange={setIsChecked} />
    );
  },
};

export const InteractiveWithLabel = {
  args: {
    labelTextON: "Servicio Activo (ON)",
    labelTextOFF: "Servicio Inactivo (OFF)",
  },

  render: (args) => {
    const [isChecked, setIsChecked] = useState(args.checked);

    useEffect(() => {
      setIsChecked(args.checked);
    }, [args.checked]);

    return (
      <div className="flex items-center space-x-2">
        <Switch
          id="airplane-mode"
          checked={isChecked}
          disabled={args.disabled}
          size={args.size}
          onCheckedChange={setIsChecked}
        />
        <Label
          htmlFor="airplane-mode"
          className={
            args.disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
          }
        >
          {isChecked ? args.labelTextON : args.labelTextOFF}
        </Label>
      </div>
    );
  },
};
