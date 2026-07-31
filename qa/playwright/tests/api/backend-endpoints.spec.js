import { test, expect } from '@playwright/test';

const API_URL = 'http://localhost:8000';

// Usar test.describe.serial para que los tests corran en orden y compartan el token
test.describe.serial('Backend API Endpoints', () => {
  test.setTimeout(30000);
  let token = ''; // Token compartido entre tests, sin race condition

  // ---- HEALTH ----
  test('GET /health debe devolver status ok', async ({ request }) => {
    const res = await request.get(`${API_URL}/health`);
    expect(res.status()).toBe(200);
    const data = await res.json();
    expect(data.status).toBe('ok');
    expect(data.service).toBe('chatbot-backend');
  });

  // ---- AUTH ----
  test('POST /api/v1/auth/login (mock) debe devolver JWT', async ({ request }) => {
    const res = await request.post(`${API_URL}/api/v1/auth/login`, {
      data: { username: 'admin', password: 'admin123' },
    });
    expect(res.status()).toBe(200);
    const data = await res.json();
    expect(data.access_token).toBeDefined();
    token = data.access_token;
  });

  // ---- CHATBOT ----
  test('GET /api/v1/chatbot/webhook verify', async ({ request }) => {
    const res = await request.get(
      `${API_URL}/api/v1/chatbot/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=my_verify_token`
    );
    expect([200, 403]).toContain(res.status());
  });

  test('POST /api/v1/chatbot/webhook receive', async ({ request }) => {
    const res = await request.post(`${API_URL}/api/v1/chatbot/webhook`, {
      data: {
        object: 'whatsapp_business_account',
        entry: [{
          id: 'TEST_ID',
          changes: [{
            value: {
              messaging_product: 'whatsapp',
              metadata: { display_phone_number: '5491112345678', phone_number_id: '123456789' },
              contacts: [{ profile: { name: 'Cliente Demo' }, wa_id: '5491123456789' }],
              messages: [{ from: '5491123456789', id: 'wamid.test123', timestamp: '1710000000', text: { body: 'Hola' }, type: 'text' }],
            },
            field: 'messages',
          }],
        }],
      },
    });
    expect(res.status()).toBe(200);
  });

  test('POST /api/v1/chatbot/chat', async ({ request }) => {
    const res = await request.post(`${API_URL}/api/v1/chatbot/chat`, {
      data: { telefono: '5491123456789', mensaje: 'Hola' },
    });
    expect(res.status()).toBe(200);
    const data = await res.json();
    expect(data.respuesta).toBeDefined();
  });

  // ---- CATALOG ----
  test('GET /api/v1/catalog/servicios/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/catalog/servicios/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  test('POST /api/v1/catalog/servicios/ (protegido)', async ({ request }) => {
    const res = await request.post(`${API_URL}/api/v1/catalog/servicios/`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { nombre: 'Test Servicio', descripcion: 'Auto test', duracion_minutos: 30, precio: 99.99 },
    });
    // Backend returns 201 Created on successful creation
    expect([200, 201]).toContain(res.status());
  });

  test('GET /api/v1/catalog/productos/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/catalog/productos/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  test('POST /api/v1/catalog/productos/ (protegido)', async ({ request }) => {
    const res = await request.post(`${API_URL}/api/v1/catalog/productos/`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { nombre: 'Test Producto', precio: 49.99, stock: 10, activo: true },
    });
    // Backend returns 201 Created on successful creation
    expect([200, 201]).toContain(res.status());
  });

  // ---- FAQ ----
  test('GET /api/v1/faq/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/faq/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  // ---- CALENDAR ----
  test('GET /api/v1/calendar/turnos/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/calendar/turnos`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  // ---- ADMIN ----
  test('GET /api/v1/admin/negocio/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/admin/negocio`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  test('GET /api/v1/admin/metrics/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/admin/metrics/?days=30&business_id=1`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  test('GET /api/v1/admin/health/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/admin/health/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  // ---- ADMIN THRESHOLDS ----
  test('GET /api/v1/admin/metric-thresholds/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/admin/metric-thresholds/?business_id=1`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  // ---- ADMIN REMINDER LOG ----
  test('GET /api/v1/admin/reminder-log/ (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/admin/reminder-log/?business_id=1`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });

  // ---- ADMIN BUSINESS CONFIG ----
  test('GET /api/v1/admin/business/1 (protegido)', async ({ request }) => {
    const res = await request.get(`${API_URL}/api/v1/admin/business/1`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(200);
  });
});