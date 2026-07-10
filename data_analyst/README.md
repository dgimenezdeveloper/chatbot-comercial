# Data_Analyst — chatbot-comercial 📊

Este directorio contiene la documentación, esquemas y diagramas relacionados con el análisis de datos, métricas y arquitectura del proyecto **chatbot-comercial**.

### nota: Controlar siempre que el contenido de este directorio refleje con precisión la realidad del proyecto, ya que es un recurso clave para el equipo de desarrollo y análisis.

## 📁 Contenido Real

| Archivo | Descripción |
|---------|-------------|
| `Documentacion_de_proyecto.md` | Documentación exhaustiva de métricas (3 escenarios, 60+ métricas, 12 críticas MVP) |
| `schema_db.md` | Esquema de base de datos con 10 modelos SQLAlchemy, índices, FK y seed data |
| `Detalles_pendientes.md` | Exploración del código backend/frontend, checklist de implementación, estado de PRs |
| `diagrama_fullstack.mmd` | Diagrama Mermaid Full Stack unificado v2.0 (Next.js + FastAPI + Google Auth + CI/CD + eventos + métricas) |
| `README.md` | Este archivo |

## 🛠️ Stack del Proyecto

### Backend
- Python 3.11+, FastAPI 0.110.0
- SQLAlchemy 2.0.28 (engine síncrono, requiere migración a async)
- Alembic 1.13.1 (configurado, sin migraciones)
- Pydantic 2.6.4, httpx 0.27.0, PyJWT 2.8.0
- PostgreSQL 15+ (principal), Redis 7+ (cache + state management)

### Frontend
- Next.js 16.2.9 (App Router), React 19.2.4
- TailwindCSS 4, shadcn/ui 4.11.0
- NextAuth v5 (beta) + Google OAuth2 Provider
- Pino logger, Storybook 10.4, Vitest 8.0
- Dockerfile Node 22-alpine

### DevOps
- Docker Compose (4 servicios: API, Frontend, PostgreSQL, Redis)
- GitHub Actions CI/CD (`.github/workflows/ci-cd.yml`)

### Integraciones
- WhatsApp Cloud API v25.0 (Meta Business)
- Google OAuth2 (backend + frontend)

## 📊 Métricas Clave (MVP)

12 métricas críticas definidas con umbrales de alerta en `Documentacion_de_proyecto.md`:

1. Tasa conversión inicio → turno (< 20% = alerta)
2. % turnos creados por bot (< 40% = alerta)
3. Tasa abandono por paso (> 40% = alerta)
4. Tasa fallback (> 25% = alerta)
5. Top 10 mensajes con fallback (roadmap)
6. % turnos nocturnos (20-8hs) (< 30% = sin valor agregado)
7. Tasa resolución autónoma (< 50% = necesita humano)
8. Tasa cancelación (> 20% = alerta)
9. Tasa no-show (> 15% = pérdida ingresos)
10. Confirmación recordatorio (< 50% = problema)
11. Servicios más reservados (ranking volumen)
12. CSAT promedio (< 3.5/5 = baja satisfacción)

## 🔔 10 Eventos a Instrumentar

`conversation_started` → `menu_option_selected` → `service_selected` → `fallback_triggered` → `appointment_created` → `escalation_to_human` → `csat_submitted` → `reminder_sent` → `reminder_response` → `conversation_closed`

**Estado:** 5/10 parcialmente instrumentados en Redis (State Manager). 5/10 pendientes. Ninguno persiste en PostgreSQL.

## 📋 Estado de PRs Mergeados a Develop

| PR | Commit | Descripción | Sincronizado |
|----|--------|-------------|-------------|
| #40 | `0b80bca` | Endpoints REST principales | ✅ |
| #43 | `121415e` | Máquina de estados WhatsApp + Redis | ✅ |
| #46 | `ade4640` | Mensajes interactivos botones/listas | ✅ |
| #47 | `c74559f` | Flujo híbrido árbol decisión + placeholder IA | ✅ |
| #48 | `6924bc2` | Google OAuth2 frontend (NextAuth v5) | ⏳ |
| #49 | `a623c5f` | Test integración auth | ⏳ |
| #50 | `431823` | CI/CD + test integración auth | ⏳ |

## 📋 Convenciones

- No subir datos sensibles al repositorio.
- Documentar cada transformación en el script correspondiente.
- Mantener actualizado el diccionario de datos en `schema_db.md`.
- Usar nomenclatura clara y consistente en los archivos (snake_case).
- Sincronizar este directorio con los cambios en develop antes de cada release.

---

> 💡 **Nota:** Este directorio fue actualizado el 8 de julio 2026 para reflejar los PRs #48, #49, #50 mergeados a develop (Google OAuth2 frontend, CI/CD, tests de integración).