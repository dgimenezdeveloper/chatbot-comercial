import { test, expect } from '@playwright/test';

test.describe('Autenticación Google OAuth', () => {

  test('debe mostrar la página de login con el botón de Google', async ({ page, context }) => {
    await context.clearCookies();
    await page.goto('/login');

    await expect(page.locator('text=Acceso Restringido')).toBeVisible();
    await expect(page.locator('button:has-text("Continuar con Google")')).toBeVisible();
    await expect(page.locator('text=Volver a la página principal')).toBeVisible();
  });
});