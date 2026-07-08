import { GoogleButton } from '@/components/auth/GoogleButton/GoogleButton';

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