import { Checkbox } from "@/components/ui/checkbox/checkbox";
import { Label } from "@/components/ui/label/label";

const meta = {
  title: "Components/UI/Checkbox",
  component: Checkbox,
  parameters: {
    layout: "centered",
  },
  argTypes: {
    defaultChecked: {
      control: "boolean",
      description: "Estado inicial del checkbox",
    },
    disabled: { control: "boolean", description: "Estado deshabilitado" },
    labelText: {
      control: "text",
      description: "Texto del componente `<Label>` adjunto",
    },
  },
};

export default meta;

export const Default = {
  args: {
    defaultChecked: false,
    disabled: false,
    labelText: "Aceptar términos y condiciones",
  },
  render: (args) => (
    <div className="flex items-center gap-2">
      <Checkbox
        id="terms-default"
        defaultChecked={args.defaultChecked}
        disabled={args.disabled}
      />
      <Label
        htmlFor="terms-default"
        className={
          args.disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
        }
      >
        {args.labelText}
      </Label>
    </div>
  ),
};

export const Checked = {
  args: {
    ...Default.args,
    defaultChecked: true,
  },
  render: Default.render,
};

export const Disabled = {
  args: {
    ...Default.args,
    defaultChecked: false,
    disabled: true,
    labelText: "Opción no disponible",
  },
  render: Default.render,
};
