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

## 🛠️ Stack de Pruebas

| Herramienta   | Propósito                                          |
|---------------|----------------------------------------------------|
| **Cypress**   | Pruebas end-to-end (E2E) del frontend              |
| **Pytest**    | Pruebas unitarias y de integración del backend     |
| **Vitest**    | Pruebas unitarias del frontend (React/TypeScript)  |

## ⚙️ Cómo Ejecutar las Pruebas

### Pruebas E2E (Cypress)

```bash
# Abrir Cypress en modo interactivo
cd frontend
npm run cypress:open
# o con yarn
yarn cypress:open

# Ejecutar pruebas en modo headless
npm run cypress:run
```

### Pruebas de Backend (Pytest)

```bash
cd backend
pytest
# Con cobertura
pytest --cov=app tests/
```

### Smoke Tests

```bash
cd qa/smoke
bash run_smoke_tests.sh
```

## 🧠 Validación de Alucinaciones del LLM

En el directorio `llm/` se encuentran estrategias y scripts para:

- Detectar respuestas inconsistentes o inventadas por el LLM.
- Validar que el contexto conversacional se mantenga dentro de los límites definidos.
- Evaluar la precisión de las respuestas contra fuentes de datos conocidas.

## 📋 Planes de Prueba

Los planes de prueba en `plans/` documentan:

- Casos de uso críticos del chatbot.
- Escenarios de flujo conversacional.
- Pruebas de regresión.
- Pruebas de carga y rendimiento.

## ✅ Convenciones

- Todas las pruebas deben pasar antes de hacer merge a `main`.
- Documentar cada bug encontrado con su respectivo test de regresión.
- Mantener los tests actualizados ante cambios en los flujos conversacionales.

---

> 💡 **Nota:** Actualiza este README con enlaces y ejemplos específicos del proyecto a medida que avance.
