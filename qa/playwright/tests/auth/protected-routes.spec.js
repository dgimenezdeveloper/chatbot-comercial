import { test, expect } from '@playwright/test';

test.describe('Rutas protegidas sin autenticación', () => {
  
  test('debe redirigir de /dashboard a /login si no hay sesión', async ({ page, context }) => {
    // Clear cookies + localStorage + sessionStorage para asegurar que no hay sesión
    await context.clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    await page.goto('/dashboard');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page.locator('text=Acceso Restringido')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('button:has-text("Continuar con Google")')).toBeVisible();
  });

  test('debe redirigir de /dashboard/agenda a /login si no hay sesión', async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });

    await page.goto('/dashboard/agenda');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page.locator('text=Acceso Restringido')).toBeVisible();
  });

  test('debe redirigir de /dashboard/servicios a /login si no hay sesión', async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });

    await page.goto('/dashboard/servicios');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page.locator('text=Acceso Restringido')).toBeVisible();
  });

  test('debe redirigir de /dashboard/clientes a /login si no hay sesión', async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });

    await page.goto('/dashboard/clientes');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page.locator('text=Acceso Restringido')).toBeVisible();
  });

  test('debe redirigir de /dashboard/configuracion a /login si no hay sesión', async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });

    await page.goto('/dashboard/configuracion');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page.locator('text=Acceso Restringido')).toBeVisible();
  });

  test('debe redirigir de /dashboard/metrics a /login si no hay sesión', async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });

    await page.goto('/dashboard/metrics');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page.locator('text=Acceso Restringido')).toBeVisible();
  });

  test('la página de login debe ser accesible sin autenticación', async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });

    await page.goto('/login');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator('button:has-text("Continuar con Google")')).toBeVisible();
  });
});