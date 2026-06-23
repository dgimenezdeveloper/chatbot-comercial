import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select";

const meta = {
  component: Select,
} satisfies Meta<typeof Select>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Select>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Seleccioná una opción" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="opcion1">Opción 1</SelectItem>
        <SelectItem value="opcion2">Opción 2</SelectItem>
        <SelectItem value="opcion3">Opción 3</SelectItem>
      </SelectContent>
    </Select>
  ),
};