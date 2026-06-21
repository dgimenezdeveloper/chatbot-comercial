import { Label } from "@/components/ui/label/label";

export default {
  title: "Components/UI/Label",
  component: Label,
  parameters: {
    layout: "centered",
  },
  argTypes: {
    children: { control: "text", description: "Texto de la etiqueta" },
  },
};

export const Base = {
  args: {
    children: "Etiqueta que acompaña a un Input",
  },
};
