import { Input } from "./input";
const meta = {
  component: Input,
};
export default meta;
export const Default = {
  args: {
    placeholder: "Type something...",
  },
};
export const Disabled = {
  args: {
    placeholder: "Disabled",
    disabled: true,
  },
};
