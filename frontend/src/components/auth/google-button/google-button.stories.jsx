import { GoogleButton } from '@/components/auth/google-button/google-button';

const meta = {
  title: 'Components/Auth/GoogleButton',
  component: GoogleButton,
  parameters: {
    layout: 'centered',
  },
};

export default meta;

export const Default = {
  args: {
    isLoading: false,
  },
};

export const Loading = {
  args: {
    isLoading: true,
  },
};