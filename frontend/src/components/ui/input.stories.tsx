import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { Input } from "./input";

const meta = {
  component: Input,
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: "Escribí algo...",
  },
};

export const Disabled: Story = {
  args: {
    placeholder: "Deshabilitado",
    disabled: true,
  },
};