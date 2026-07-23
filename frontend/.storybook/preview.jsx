/** @type { import('@storybook/nextjs-vite').Preview } */
import "../src/app/globals.css";
import React, { useEffect } from "react";

const preview = {
  tags: ["autodocs"],
  parameters: {
    backgrounds: {
      default: "light",
      disable: true,
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
      disableSaveFromUI: true,
    },
  },
  decorators: [
    (Story) => {
      useEffect(() => {
        document.documentElement.classList.add("theme-app");
        document.documentElement.style.setProperty("--font-geist-sans", "system-ui, -apple-system, sans-serif");
        document.documentElement.style.setProperty("--font-geist-mono", "ui-monospace, monospace");
      }, []);

      return (
        <div className="bg-surface p-8 text-foreground antialiased">
          <Story />
        </div>
      );
    },
  ],
};

export default preview;