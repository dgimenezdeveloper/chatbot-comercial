/** @type { import('@storybook/nextjs-vite').Preview } */
import "../src/app/globals.css";

const preview = {
  tags: ["autodocs"],
  parameters: {
    backgrounds: {
      default: "light",
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
      disableSaveFromUI: true,
    },
    a11y: {
      test: "todo",
    },
  },
};

export default preview;
