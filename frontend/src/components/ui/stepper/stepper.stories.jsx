import Stepper from "./stepper";

const steps = [
  {
    number: 1,
    label: "Tu Negocio",
  },
  {
    number: 2,
    label: "Horarios",
  },
];

const meta = {
  title: "Components/UI/Stepper",
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    steps: {
      control: "object",
    },
    currentStep: {
      control: {
        type: "number",
        min: 1,
        max: steps.length,
      },
    },
  },
};

export default meta;

const Template = (args) => (
  <div className="w-64">
    <Stepper {...args} />
  </div>
);

export const FirstStep = {
  args: {
    steps,
    currentStep: 1,
  },
  render: Template,
};

export const SecondStep = {
  args: {
    steps,
    currentStep: 2,
  },
  render: Template,
};

export const Interactive = {
  args: {
    steps,
    currentStep: 1,
  },
  render: Template,
};