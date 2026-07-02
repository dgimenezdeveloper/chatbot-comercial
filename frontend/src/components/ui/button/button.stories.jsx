import  { Meta, StoryObj } from "@storybook/nextjs-vite";
import { Button } from "./button";

const meta = {
  component: Button,
};

export default meta;

export const Default = {
  args: {
    children: "Button",
  },
};

export const Secondary = {
  args: {
    children: "Button",
    variant: "secondary",
  },
};

export const Disabled = {
  args: {
    children: "Button",
    disabled: true,
  },
};
