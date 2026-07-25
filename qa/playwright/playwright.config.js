import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  testDir: './tests',
  timeout: 60000,
  expect: { timeout: 10000 },
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    // Frontend tests — Chrome visible with slowMo for visual inspection
    {
      name: 'chrome',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        headless: false,
        launchOptions: { slowMo: 300 },
      },
      testMatch: ['**/*.spec.js'],
      testIgnore: ['**/api/**'],
    },
    // Backend API tests — headless, no browser UI needed
    {
      name: 'api',
      use: { headless: true },
      testMatch: ['**/api/**'],
    },
  ],
  reporter: [['html'], ['list']],
});