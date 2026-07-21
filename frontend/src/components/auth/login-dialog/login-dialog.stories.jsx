import React from "react";
import { LoginDialog } from "@/components/auth/login-dialog/login-dialog";
import { Button } from "@/components/ui/button/button";

const meta = {
  title: "Components/Auth/LoginDialog",
  component: LoginDialog,
  parameters: {
    layout: "centered",
  },
};

export default meta;

export const Default = {
  render: () => (
    <LoginDialog>
      <Button variant="outline">Ingresar</Button>
    </LoginDialog>
  ),
};
