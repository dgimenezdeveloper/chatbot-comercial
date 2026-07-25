# QA — chatbot-comercial 🧪

Este directorio contiene los planes de prueba, scripts de automatización y estrategias de calidad del proyecto **chatbot-comercial**.

## 📁 Contenido

| Directorio / Archivo       | Descripción                                              |
|----------------------------|----------------------------------------------------------|
| `e2e/`                     | Pruebas end-to-end con Cypress                           |
| `api/`                     | Pruebas de API con Pytest (Backend)                      |
| `smoke/`                   | Smoke tests para validación rápida post-despliegue       |
| `llm/`                     | Estrategias de validación de alucinaciones del LLM       |
| `plans/`                   | Planes de prueba y casos de uso documentados             |
| `playwright/`              | Pruebas E2E con Playwright (frontend + backend API)      |

## 🛠️ Stack de Pruebas

| Herramienta   | Propósito                                          |
|---------------|----------------------------------------------------
| **Pytest**    | Pruebas unitarias y de integración del backend     |
| **Vitest**    | Pruebas unitarias del frontend (React/TypeScript)  |
| **Playwright**  | Pruebas E2E con browser automation + tests de API  |

## ⚙️ Cómo Ejecutar las Pruebas

### Pruebas Playwright

```bash
cd qa/playwright

# Instalar dependencias
pnpm install

# Configurar variables de entorno (solo URLs)
cp .env.example .env

# Ejecutar todos los tests
pnpm test

# Solo tests de frontend (Chrome visible)
pnpm test --project=chrome

# Solo tests de backend (headless, sin navegador)
pnpm test --project=api

# Test manual paso a paso (requiere intervención humana)
pnpm test:flow

# Modo UI interactivo (recomendado para debugging)
pnpm test:ui

# Ver reporte HTML
pnpm report
```

#### Estructura de tests

| Directorio | Contenido |
|-----------|-----------|
| `tests/auth/` | Tests de frontend: página de login + rutas protegidas |
| `tests/api/` | Tests de backend: 15 endpoints (health, auth, chatbot, catalog, faq, calendar, admin) |
| `tests/auth/full-flow.js` | Script manual: Landing → Login Google → Dashboard → Logout |

#### Requisitos
- Backend corriendo en `http://localhost:8000`
- Frontend corriendo en `http://localhost:3000`
- **Google OAuth**: El login completo requiere intervención manual (`pnpm test:flow`) porque Google bloquea navegadores automatizados. Los tests automatizados verifican redirección de rutas protegidas sin necesidad de login.

## ✅ Convenciones

- Todas las pruebas deben pasar antes de hacer merge a `main`.
- Documentar cada bug encontrado con su respectivo test de regresión.
- Mantener los tests actualizados ante cambios en los flujos conversacionales.

---

> 💡 **Nota:** Actualiza este README con enlaces y ejemplos específicos del proyecto a medida que avance.