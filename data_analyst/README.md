# Data_Analyst — chatbot-comercial 📊

Este directorio contiene la documentación, esquemas y diagramas relacionados con el análisis de datos, métricas y arquitectura del proyecto **chatbot-comercial**.

> **Nota:** Controlar siempre que el contenido de este directorio refleje con precisión la realidad del proyecto, ya que es un recurso clave para el equipo de desarrollo y análisis.

## 📁 Contenido Real

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Este archivo |
| `Documentacion_de_proyecto.md` | Documentación exhaustiva de métricas (3 escenarios, 60+ métricas, 12 críticas MVP) |
| `schema_db.md` | Esquema de base de datos con 12 modelos SQLAlchemy, índices, FK y seed data |
| `diagrama_fullstack.mmd` | Diagrama Mermaid Full Stack unificado v2.1 (Next.js + FastAPI + Google Auth + CI/CD + Celery + métricas + eventos) |

### 📚 Documentación complementaria en `repositorio/docs/`

| Archivo | Descripción |
|---------|-------------|
| `user-guide-metrics.md` | Guía para el dueño del negocio: qué significan las métricas, los recordatorios y los colores de alerta |
| `deploy.md` | Pasos para desplegar la aplicación en un entorno nuevo o reconstruir desde cero |
| `tech-debt.md` | Deuda técnica documentada: operadores PostgreSQL, decisión CSAT data flow |


## 📊 Métricas Clave (MVP)

12 métricas críticas definidas con umbrales de alerta configurables por negocio en `Documentacion_de_proyecto.md`:

1. Tasa conversión inicio → turno (< 20% = alerta)
2. Porcentajes de turnos creados por bot (< 40% = alerta)
3. Tasa abandono por paso (> 40% = alerta)
4. Tasa fallback (> 25% = alerta)
5. Top 10 mensajes con fallback (roadmap)
6. Porcentajes de turnos nocturnos (20-8hs) (< 30% = sin valor agregado)
7. Tasa resolución autónoma (< 50% = necesita humano)
8. Tasa cancelación (> 20% = alerta)
9. Tasa no-show (> 15% = pérdida ingresos)
10. Confirmación recordatorio (< 50% = problema)
11. Servicios más reservados (ranking volumen)
12. CSAT promedio (< 3.5/5 = baja satisfacción)

**Total:** 50 métricas implementadas (12 MVP + 38 extendidas en 9 casos de uso)

## 🔔 10 Eventos Instrumentados

`conversation_started` → `menu_option_selected` → `service_selected` → `fallback_triggered` → `appointment_created` → `escalation_to_human` → `csat_submitted` → `reminder_sent` → `reminder_response` → `conversation_closed`

**Estado:** ✅ 10/10 eventos instrumentados con `event_logger.log_event()`. Todos persisten en PostgreSQL vía tabla `event`. El evento `csat_submitted` además escribe en `feedback` como fuente canónica de métricas CSAT.

## ⏰ Recordatorios Automáticos (Celery)

- Scheduler Celery Beat programado a las 9 AM (hora Buenos Aires), una vez por día
- 4 niveles de fallback: template pago Meta → ventana 24h WhatsApp → canal alternativo → notificar al dueño
- Trazabilidad completa vía `ReminderLog`

## 📋 Convenciones

- No subir datos sensibles al repositorio.
- Documentar cada transformación en el script correspondiente.
- Mantener actualizado el diccionario de datos en `schema_db.md`.
- Usar nomenclatura clara y consistente en los archivos (snake_case).
- Sincronizar este directorio con los cambios en develop antes de cada release.

---