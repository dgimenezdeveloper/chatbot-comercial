/**
 * 🔧 SCRIPT MANUAL — NO ES UN TEST AUTOMATIZADO
 *
 * Este es un helper interactivo para desarrollo local y debugging visual.
 * Requiere intervención humana (readline) y NO puede ejecutarse en CI.
 *
 * Para tests automatizados, usar: pnpm test
 * Para este script manual: pnpm test:flow
 *
 * Flujo: Landing → Ingresar → Modal Google → Google Auth → Dashboard → Cerrar sesión
 */

import { chromium } from 'playwright';
import { createInterface } from 'readline';

const BASE_URL = 'http://localhost:3000';

async function run() {
  console.log('');
  console.log('========================================');
  console.log('  TEST MANUAL PASO A PASO');
  console.log('  (Script interactivo — solo desarrollo local)');
  console.log('========================================');
  console.log('');

  const context = await chromium.launchPersistentContext('/tmp/playwright-chrome-profile', {
    channel: 'chrome',
    headless: false,
    viewport: { width: 1280, height: 720 },
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check'],
  });

  const page = context.pages()[0] || await context.newPage();

  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    window.chrome = { runtime: {} };
  });

  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const enter = () => new Promise(r => rl.once('line', r));

  // PASO 1: Landing page
  console.log('📱 PASO 1: Abriendo localhost:3000...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  console.log('   ✅ Landing page cargada');
  await page.waitForTimeout(500);

  // PASO 2: Click en el botón "Ingresar" (button, no link)
  console.log('📱 PASO 2: Click en botón "Ingresar"...');
  // The button has data-slot="button" and text "Ingresar"
  await page.click('button:has-text("Ingresar")');
  console.log('   ✅ Botón "Ingresar" clickeado');
  await page.waitForTimeout(500);

  // PASO 3: Esperar el modal con "Continuar con Google"
  console.log('📱 PASO 3: Esperando modal con "Continuar con Google"...');
  await page.waitForSelector('button:has-text("Continuar con Google")', { timeout: 5000 });
  console.log('   ✅ Modal abierto - botón Google visible');

  // PASO 4: Click en "Continuar con Google"
  console.log('📱 PASO 4: Click en "Continuar con Google"...');
  await page.click('button:has-text("Continuar con Google")');

  // ESPERAR NAVEGACIÓN: puede ir a Google, directo al dashboard, o pedir login manual
  console.log('📱 PASO 5: Esperando redirección...');
  await page.waitForTimeout(3000);
  let url = page.url();

  // Si ya estamos en el dashboard, Google nos reconoció sin pedir account chooser
  if (url.includes('dashboard')) {
    console.log('   ✅ Google te reconoció — directo al dashboard');
  } else if (url.includes('accounts.google.com')) {
    // Flujo normal: estamos en Google (account chooser o login)
    console.log('   ✅ Google cargado — intentando automatizar...');
    await page.waitForTimeout(2000);

    // Intentar seleccionar cuenta
    const accountEl = page.locator('[data-email], div[role="link"][data-identifier]').first();
    if (await accountEl.isVisible({ timeout: 2000 }).catch(() => false)) {
      await accountEl.click();
      console.log('   ✅ Cuenta seleccionada');
    } else {
      console.log('   ⚠️  No se detectó lista de cuentas. Si es primera vez, completá el login:');
      console.log('       Email → Siguiente → Password → Siguiente');
    }
    await page.waitForTimeout(2000);

    // Intentar confirmar permisos
    const confirmBtn = page.locator('button:has-text("Continuar"), button:has-text("Continue"), button:has-text("Siguiente"), button:has-text("Next")').first();
    for (let i = 0; i < 2; i++) {
      if (await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await confirmBtn.click();
        console.log('   ✅ Confirmación aceptada');
        await page.waitForTimeout(2000);
      }
    }

    // Esperar dashboard (puede fallar si hay que completar login manual)
    try {
      await page.waitForURL('**/dashboard/**', { timeout: 10000 });
      console.log('   ✅ Redirigido al dashboard');
    } catch {
      console.log('   ⏳ Todavía en Google...');
    }
  }

  // Si no llegamos al dashboard, pausa para login manual
  url = page.url();
  console.log(`📱 PASO 6: URL → ${url}`);
  if (!url.includes('dashboard')) {
    console.log('');
    console.log('   ⏸️  PAUSA — Completá el login manualmente.');
    console.log('   (Si Google pide email/password, ingresalos ahora)');
    console.log('   Cuando veas el dashboard, presioná ENTER...');
    console.log('');
    await enter();
    url = page.url();
  }

  if (!url.includes('dashboard')) {
    console.log('   ❌ No se llegó al dashboard.');
    rl.close();
    await context.close();
    process.exit(1);
  }

  console.log('📱 PASO 7: Verificando autenticación...');
  try {
    await page.waitForSelector('text=Tu negocio', { timeout: 5000 });
    console.log('   ✅ "Tu negocio" visible — autenticación exitosa');
  } catch {
    console.log('   ⚠️  Dashboard cargado');
  }

  // PASO 8: Cerrar sesión desde el sidebar
  console.log('📱 PASO 8: Cerrando sesión...');
  
  // Hacer clic en el <span>Cerrar sesión</span> del sidebar
  await page.click('span:has-text("Cerrar sesión")');
  console.log('   ✅ Click en "Cerrar sesión"');
  await page.waitForTimeout(1500);

  // PASO 9: Cerrar Chrome
  console.log('📱 PASO 9: Cerrando Chrome...');
  await context.close();

  console.log('');
  console.log('========================================');
  console.log('  ✅ TEST COMPLETADO');
  console.log('========================================');
  console.log('  Landing → Ingresar → Modal Google → Google Auth → Dashboard → Cerrar sesión');
  console.log('  Chrome cerrado correctamente.');

  rl.close();
}

run().catch(e => {
  console.error('❌', e);
  process.exit(1);
});
