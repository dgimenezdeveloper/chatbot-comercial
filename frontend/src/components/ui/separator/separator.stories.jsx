import React from "react";
import { Separator } from "@/components/ui/separator/separator";

export default {
  title: "Components/UI/Separator",
  component: Separator,
  parameters: {
    layout: "centered",
  },
  argTypes: {
    orientation: {
      control: "select",
      options: ["horizontal", "vertical"],
      description: "Orientación física del separador",
    },
    decorative: {
      control: "boolean",
      description:
        "Si es verdadero, se ignora por las tecnologías de asistencia",
    },
  },
  args: {
    orientation: "horizontal",
    decorative: true,
  },
};

// 1. Base (Horizontal): Forzamos altura de 2px (h-0.5) y color más oscuro
export const Base = {
  render: (args) => (
    <div className="w-64">
      <Separator {...args} className="h-0.5 bg-gray-400" />
    </div>
  ),
};

// 2. Vertical: Forzamos ancho de 2px (w-0.5), alto fijo y color más oscuro
export const Vertical = {
  args: {
    orientation: "vertical",
  },
  render: (args) => (
    <div className="h-16 flex items-center justify-center">
      <Separator {...args} className="w-0.5 h-full bg-gray-400" />
    </div>
  ),
};

// 3. ListSeparator
export const ListSeparator = {
  render: (args) => (
    <div className="w-64 text-center">
      <p className="text-sm text-muted-foreground">Contenido Superior</p>
      <Separator {...args} className="my-4 h-0.5 bg-gray-400" />
      <p className="text-sm text-muted-foreground">Contenido Inferior</p>
    </div>
  ),
};

// 4. MenuSeparator
export const MenuSeparator = {
  args: {
    orientation: "vertical",
  },
  render: (args) => (
    <div className="flex h-5 items-center space-x-4 text-sm">
      <div>Docs</div>
      <Separator {...args} className="w-0.5 h-full bg-gray-400" />
      <div>Source</div>
      <Separator {...args} className="w-0.5 h-full bg-gray-400" />
      <div>Core</div>
    </div>
  ),
};
