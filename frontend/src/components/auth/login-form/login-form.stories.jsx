import { LoginForm } from "@/components/auth/login-form/login-form";

const meta = {
  title: "Components/Auth/LoginForm",
  component: LoginForm,
};

export default meta;

export const Default = {
  args: {
    isGoogleLoading: false,
  },
};

export const LoadingGoogle = {
  args: {
    isGoogleLoading: true,
  },
};