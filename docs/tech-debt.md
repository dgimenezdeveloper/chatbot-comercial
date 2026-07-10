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
