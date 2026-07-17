import React from "react";
import { LoginDialog } from "@/components/auth/login-dialog/login-dialog";
import { Dialog } from "@/components/ui/dialog/dialog";

const meta = {
  title: "Components/Auth/LoginDialog",
  component: LoginDialog,
  parameters: {
    layout: "centered",
  },
};

export default meta;

export const Default = {
  render: () => <LoginDialog />,
};
