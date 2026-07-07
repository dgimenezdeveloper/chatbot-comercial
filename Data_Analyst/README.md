# Data_Analyst — chatbot-comercial 📊

Este directorio contiene la documentación, esquemas y diagramas relacionados con el análisis de datos y métricas del proyecto **chatbot-comercial**.

### nota: Controlar siempre que el contenido de este directorio refleje con precisión la realidad del proyecto, ya que es un recurso clave para el equipo de desarrollo y análisis.

## 📁 Contenido Real

| Archivo | Descripción |
|---------|-------------|
| `Documentacion_de_proyecto.md` | Documentación exhaustiva de métricas (3 escenarios, 60+ métricas, 12 críticas MVP) |
| `schema_db.md` | Esquema de base de datos con 10 modelos SQLAlchemy, índices, FK y seed data |
| `Detalles_pendientes.md` | Exploración del código backend/frontend, checklist de implementación |
| `diagrama_fullstack.mmd` | Diagrama Mermaid Full Stack unificado (Next.js + FastAPI + eventos + métricas) |
| `README.md` | Este archivo |

## 🛠️ Stack del Proyecto

- **Backend:** Python 3.11+, FastAPI 0.110.0, SQLAlchemy 2.0.28, Alembic 1.13.1
- **Frontend:** Next.js 16, React 19, TailwindCSS 4, shadcn/ui
- **DB:** PostgreSQL 15+ (principal), Redis 7+ (cache)
- **Integración:** WhatsApp Cloud API (Meta Business)

## 📊 Métricas Clave (MVP)

12 métricas críticas definidas con umbrales de alerta en `Documentacion_de_proyecto.md`:

1. Tasa conversión inicio → turno
2. % turnos creados por bot
3. Tasa abandono por paso
4. Tasa fallback
5. Top 10 mensajes con fallback
6. % turnos nocturnos (20-8hs)
7. Tasa resolución autónoma
8. Tasa cancelación
9. Tasa no-show
10. Confirmación recordatorio
11. Servicios más reservados
12. CSAT promedio

## 🔔 10 Eventos a Instrumentar

`conversation_started` → `menu_option_selected` → `service_selected` → `fallback_triggered` → `appointment_created` → `escalation_to_human` → `csat_submitted` → `reminder_sent` → `reminder_response` → `conversation_closed`

## 📋 Convenciones

- No subir datos sensibles al repositorio.
- Documentar cada transformación en el script correspondiente.
- Mantener actualizado el diccionario de datos en `schema_db.md`.
- Usar nomenclatura clara y consistente en los archivos (snake_case).

---

> 💡 **Nota:** Este directorio fue actualizado el 7 de julio 2026 para reflejar con precisión el contenido real.