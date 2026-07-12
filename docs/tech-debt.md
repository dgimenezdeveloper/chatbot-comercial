# Deuda Técnica — data-models-metrics

## PostgreSQL-specific Operators

Las siguientes queries en `metrics_queries.py` usan operadores específicos de PostgreSQL que no son compatibles con SQLite:

| Métrica | Operador | Línea | Descripción |
|---------|----------|-------|-------------|
| M6 (nocturnal) | `EXTRACT(HOUR FROM ...)` | ~L190 | Extrae la hora de un timestamp |
| M10 (reminder) | `EXTRACT(EPOCH FROM ...)` | ~L360 | Calcula diferencia en segundos |
| M4 (fallback) | `func.jsonb_array_length()` | ~L140 | Cuenta elementos en JSONB array |

### Impacto
- Las pruebas unitarias con SQLite fallarán para estas métricas
- No hay equivalente portable entre SQLite y PostgreSQL para estos operadores

### Plan de acción
1. Corto plazo: documentar en este archivo (hecho)
2. Mediano plazo: crear fixtures de PostgreSQL en CI para tests de integración
3. Largo plazo: evaluar `testcontainers-python` para levantar PostgreSQL real en tests

### Notas
- El resto de las queries usan SQLAlchemy estándar y son portables
- Los operadores JSONB son correctos para el stack actual (PostgreSQL 16)
- No se recomienda abstraerlos — se perdería type safety y performance

---

## Decisión CSAT Data Flow — chatbot-mvp-completion

**Contexto:** Cuando un cliente califica al bot (1-5 estrellas) vía WhatsApp, el webhook
genera un evento `csat_submitted` en la tabla `event`. La métrica M12 (`csat_average`)
lee de la tabla `feedback`, no de `event`. Esto causaba que el CSAT siempre retornara 0.

**Opciones evaluadas:**

| Opción | Descripción | Resultado |
|--------|-------------|-----------|
| **A** | Modificar `get_csat_average()` (M12) para leer de `event` como fallback cuando `feedback` está vacío | ❌ Rechazada. Mezcla fuentes de datos y complica la query |
| **B** | Escribir en `feedback` dentro del handler `csat_submitted` del webhook | ✅ Elegida |

**Decisión:** Opción B. El handler `csat_submitted` ahora escribe en ambas tablas:
- `event`: trazabilidad (no se toca, comportamiento existente)
- `feedback`: fuente canónica de métricas CSAT (nuevo)

**Ventajas:**
- Una sola fuente de verdad (`feedback`) para métricas
- Sin cambios en `get_csat_average()` — sigue funcionando igual
- Trazabilidad intacta en `event`

**Fecha:** 2026-07-11
**Feature:** chatbot-mvp-completion, FR-E2
