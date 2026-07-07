import { LoginForm } from "@/components/auth/LoginForm/LoginForm";

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