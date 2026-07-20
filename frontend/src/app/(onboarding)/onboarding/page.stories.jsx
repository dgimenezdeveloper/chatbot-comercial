import OnboardingPage from "@/app/(onboarding)/onboarding/page";

const meta = {
  title: "Pages/Onboarding/BusinessPage",
  component: OnboardingPage,

  parameters: {
    layout: "fullscreen",
  },

  decorators: [
    (Story) => (
      <div className="min-h-screen bg-white p-6 sm:p-8 lg:p-12">
        <Story />
      </div>
    ),
  ],
};

export default meta;

/**
 * Renderiza la página completa del primer paso.
 *
 * Esta historia usa el estado y la validación reales
 * definidos en page.jsx.
 */
export const Default = {};