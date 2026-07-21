# Detalles Pendientes - Exploración del Proyecto Chatbot Comercial

**Fecha:** 12 de julio 2026
**Estado:** chatbot-mvp-completion implementado — 50 métricas, scheduler Celery, umbrales configurables, CSAT fix, 73 tests. Code review Grade A.
**Rama actual:** features/data-models (PR #58 abierto → develop)
**Nota:** Prioridades 1, 2, 3 y 4 del plan original RESUELTAS. Pendiente: ejecutar migraciones + verificación Docker end-to-end.

---

## 📁 Estructura Explorada del Backend

### **Backend API (FastAPI)** ✅ Completado

#### **Archivo: `/backend/app/main.py`**
- **Estado:** Implementado con routers definidos
- **Routers activados:**
  - `/api/v1/auth` - Autenticación (JWT + Google OAuth2)
  - `/api/v1/chatbot` - Chatbot (webhook + chat)
  - `/api/v1/catalog` - Productos/Servicios (protegido con JWT)
  - `/api/v1/faq` - Preguntas frecuentes (protegido con JWT)
  - `/api/v1/calendar` - Gestión de turnos (protegido con JWT)
  - `/api/v1/admin` - Panel administrativo (protegido con JWT)

#### **Archivo: `/backend/app/api/v1/chatbot/webhook.py`**
- **Estado:** ✅ COMPLETO — State Router con 8 handlers específicos
- **Implementaciones:**
  - GET verify + POST receive para Meta WhatsApp Cloud API
  - State Router con if/elif basado en user_state (Redis)
  - Estados: INITIAL, MENU_SELECTION, SERVICE_SELECTION, DATE_SELECTION, TIME_SELECTION, CONFIRMATION, FALLBACK_1, FALLBACK_2, HUMAN_ESCALATION
  - Soporte para mensajes interactivos (botones y listas)
  - Flujo híbrido árbol de decisión MVP + placeholder IA
  - Fallback handling: 2 intentos → escalamiento a humano

#### **Archivo: `/backend/app/services/whatsapp.py`**
- **Estado:** ✅ COMPLETO
- **Funciones:** `send_message`, `send_interactive_buttons`, `send_interactive_list`
- **Integración:** Meta WhatsApp Cloud API v25.0

#### **Archivo: `/backend/app/services/state_manager.py`**
- **Estado:** ✅ COMPLETO
- **Funciones:** `get_user_state`, `set_user_state`, `clear_user_state`
- **Backend:** Redis 7+ con TTL configurable

#### **Archivo: `/backend/app/core/security.py`**
- **Estado:** ✅ COMPLETO
- **Implementaciones:** JWT token generation/validation + Google OAuth2 verification

#### **Archivo: `/backend/app/core/settings.py`**
- **Estado:** ✅ Configurado con 19 variables de entorno
- **Incluye:** DATABASE_URL, REDIS_URL, WhatsApp credentials, JWT secrets, Google OAuth2

---

## 🗄️ Capa de Datos y Servicios

### **Modelos de Datos (DB)** - `/backend/app/db/models/`
✅ **COMPLETO — 12 modelos SQLAlchemy.** 10 modelos base + 2 nuevos en chatbot-mvp-completion:

| Archivo | Modelo | Features clave |
|---------|--------|----------------|
| `business.py` | Business | Raíz multi-tenant, slug único, config WhatsApp, **+use_whatsapp_templates, +owner_phone** (nuevo) |
| `user.py` | User | Roles admin/operator/guest, UniqueConstraint(phone, business_id) |
| `service.py` | Service | Catálogo con categorías y precios, composite PK (id, business_id) |
| `product.py` | Product | Productos con stock y costo, índice parcial is_active |
| `appointment.py` | Appointment | Turnos con 3 enums, composite PK, **+notification_sent_at** |
| `faq.py` | FAQ | Preguntas frecuentes categorizadas con orden |
| `events.py` | Event | Eventos con JSONB payload, GIN index, FK a session |
| `sessions.py` | ChatSession | Sesiones con métricas agregadas (n_messages, n_fallbacks) |
| `feedback.py` | Feedback | CSAT 1-5 con outcome de interacción |
| `turno_apuesta.py` | TurnoApuesta | Gamificación de apuestas diarias |
| `metric_threshold.py` | MetricThreshold | **NUEVO** — Umbrales warning/critical configurables por negocio |
| `reminder_log.py` | ReminderLog | **NUEVO** — Trazabilidad de intentos de envío de recordatorios |

Todos con índices de rendimiento, docstrings en español, y `ondelete` consistente.

### **Services de Negocio** - `/backend/app/services/`
- ✅ `whatsapp.py` — Integración con WhatsApp Cloud API v25.0
- ✅ `state_manager.py` — Redis State Manager
- ✅ `catalog.py` — CRUD servicios/productos con soft-delete + validación whitelist
- ✅ `calendar.py` — Gestión de turnos: crear, listar, cancelar, actualizar estado
- ✅ `negocio.py` — Orquestación: get_or_create_user, slots disponibles
- ✅ `faq.py` — CRUD FAQs con búsqueda ILIKE
- ✅ `event_logger.py` — log_event() fire-and-forget para 10+ eventos
- ✅ `metrics_queries.py` — **50 métricas** (12 MVP + 38 extendidas) con get_all_metrics()

### **Scheduler de Recordatorios** ✅ COMPLETO
- ✅ Celery configurado (`app/scheduler/config.py` + `app/scheduler/tasks.py`)
- ✅ `send_reminders()` — 4 niveles de fallback: templates pagos → ventana 24h → canal alternativo → notificar dueño
- ✅ Filtro `notification_sent_at IS NULL` para evitar duplicados
- ✅ Celery Beat programado a las 9 AM (hora de Buenos Aires), una vez por día
- ✅ Un solo `asyncio.run()` para todos los envíos (no un event loop por turno)
- ✅ `ReminderLog` registra cada intento con status/channel/error_reason
- ✅ `GET /api/v1/admin/reminder-log` + `GET /api/v1/admin/health`
- ✅ Servicios `celery-worker` + `celery-beat` en `docker-compose.yml` (6 servicios totales, usan el Dockerfile del backend)
- ⚠️ Sin WhatsApp real no se puede validar la entrega del mensaje, pero todo el pipeline de errores/rollback/log está probado con tests

### **Migrations Alembic**
- ⏳ **No ejecutado aún** — requiere PostgreSQL corriendo (`docker compose up -d db redis`)
- ✅ Alembic configurado (`alembic.ini`, `env.py`, `script.py.mako`)
- ✅ `Base.metadata` incluye los 12 modelos
- 📋 Pasos pendientes: `alembic revision --autogenerate` → `alembic upgrade head` → `python -m app.data_seed`

---

## 📋 Estructura Explorada del Frontend

### **Frontend (Next.js 16 + React 19)** ✅ Parcialmente completado

#### **Rutas del App Router:**
- ✅ `(landingpage)/` - Landing page pública con layout + página principal
- ✅ `(marketing)/` - Marketing page (legacy)
- ✅ `(auth)/` - Login + Register con layout y stories
- ✅ `(dashboard)/` - Dashboard + Onboarding con stories

#### **Autenticación (NUEVO - PR #48):**
- ✅ `src/auth.js` - NextAuth v5 config con Google Provider + backend token exchange
- ✅ `src/app/api/auth/[...nextauth]/route.js` - Route handlers GET/POST
- ✅ `components/auth/google-button/` - GoogleButton component + stories
- ✅ `components/auth/login-form/` - LoginForm component + stories

#### **Componentes (NUEVO - PR #48):**
- ✅ `components/landing-page/` - 5 secciones: hero, features, how-to, onboarding, contact
- ✅ `components/layout/` - Navbar + Footer

#### **UI Components (shadcn/ui):**
- ✅ badge, button, card, checkbox, input, label, select, separator, switch, table (10 componentes)

#### **Librerías y Utilidades (NUEVO - PR #48):**
- ✅ `src/lib/logger.js` - Pino logger para traceo
- ✅ `src/proxy.js` - API proxy configuration
- ✅ `frontend/Dockerfile` - Node 22-alpine container
- ✅ `frontend/.env.example` - Variables de entorno frontend

#### **CI/CD (NUEVO - PR #50):**
- ✅ `.github/workflows/ci-cd.yml` - Lint + Test + Build + Deploy pipeline

---

## 🔑 Estado de Funcionalidades del Chatbot

### Caso de uso 1: Agendar turno nuevo ⚠️ Parcial (gap de integración)
- ✅ State Router con 8 handlers (Redis)
- ✅ Soporte para mensajes interactivos (botones/listas)
- ✅ Flujo híbrido árbol de decisión + placeholder IA
- ✅ `calendar.py` tiene `create_appointment()` listo para persistir en PostgreSQL
- ❌ **El webhook NO llama a `create_appointment()`** — solo loguea eventos JSON, no crea filas `Appointment`
- ❌ Sin filas reales, el scheduler Celery no tiene turnos que recordar

### Caso de uso 2: Modificar turno existente ❌ No implementado
- ❌ Buscar turno por usuario (calendar tiene `get_appointments_by_phone`, no usado en webhook)
- ❌ Disponibilidad para re-agendar
- ❌ Confirmación del cambio

### Caso de uso 3: Cancelar turno ⚠️ Backend listo, no integrado en webhook
- ✅ `calendar.py` tiene `cancel_appointment(appointment_id, motivo)` con soft-delete
- ❌ El webhook no tiene handler de cancelación que llame a `cancel_appointment`
- ❌ `btn_turno_cancelar` definido en UI pero su handler solo muestra texto informativo

### Caso de uso 4: Recordatorio automático T-24hs ✅ Scheduler implementado
- ✅ Celery Worker + Beat programado a las 9 AM diario
- ✅ 4 niveles de fallback: templates → ventana 24h → canal alternativo → notificar dueño
- ✅ Filtro `notification_sent_at IS NULL` para evitar duplicados
- ✅ `ReminderLog` registra cada intento
- ⚠️ **Bloqueado por Caso de uso 1**: sin filas `Appointment` reales, el scheduler no encuentra nada
- ⚠️ Sin token de WhatsApp real, `send_message()` falla, pero el pipeline de errores está probado

### Caso de uso 5: Consultar disponibilidad sin agendar ❌ No implementado
- ❌ Mostrar slots disponibles por día/hora
- ❌ Filtrado por servicio
- 📋 **Complejidad PRD: baja/media** (ver análisis abajo)

### Caso de uso 6: Consultar precios ❌ No implementado
- ❌ El `catalog.py` tiene CRUD de servicios con precios pero no expuesto al webhook

### Caso de uso 7: Consultar profesionales/empleados ❌ No implementado
- ❌ No existe modelo de profesionales aún

### Caso de uso 8: Interacción bot vs escalamiento ✅ Parcial
- ✅ Lógica de fallback implementada (FALLBACK_1 → FALLBACK_2 → HUMAN_ESCALATION)
- ✅ Escalamiento automático tras 2 fallbacks consecutivos
- ⚠️ Notificación al humano no implementada

---

## 📊 Infraestructura y DevOps

### Docker Compose ✅ Completo (6 servicios)
- ✅ `api` — Backend FastAPI (:8000)
- ✅ `db` — PostgreSQL 16-alpine (:5432)
- ✅ `redis` — Redis 7-alpine (:6379)
- ✅ `celery-worker` — Celery worker (mismo Dockerfile del backend)
- ✅ `celery-beat` — Celery scheduler periódico (9 AM)
- ✅ `frontend` — Next.js (:3000)
- ⚠️ Requiere `sudo mkdir -p /var/tmp/chatbot_postgres_data /var/tmp/chatbot_redis_data` antes de levantar (volúmenes bind mount)

### CI/CD ✅ Implementado
- ✅ GitHub Actions workflow (`.github/workflows/ci-cd.yml`)
- ✅ Pipeline: Lint + Test + Build + Deploy

---

## 🔑 Eventos a Instrumentar (10 Base)

✅ **IMPLEMENTADO en PR #58.** Los 10 eventos están instrumentados con `log_event()`:

| Evento | Estado | Momento de disparo | Campos necesarios |
|--------|--------|-------------------|------------------|
| `conversation_started` | ✅ Persiste en PostgreSQL | Primer mensaje usuario | session_id, business_id, timestamp, channel, is_new_user |
| `menu_option_selected` | ✅ Persiste en PostgreSQL | Usuario elige opción | session_id, option_name |
| `service_selected` | ✅ Persiste en PostgreSQL | Confirma servicio | service_id, confidence_score |
| `fallback_triggered` | ✅ Persiste en PostgreSQL | Bot no entiende | message_original, previous_state, fallback_n |
| `appointment_created` | ✅ Persiste en PostgreSQL | Turno confirmado | appointment_id, via_bot=true, duration_flujo_seg, horario_nocturno |
| `escalation_to_human` | ✅ Persiste en PostgreSQL | Escala a humano | reason, n_fallbacks_previos, current_flow_state |
| `csat_submitted` | ✅ Persiste en PostgreSQL (fix C1) | Usuario califica | score 1-5, outcome (turno/escalado/abandonado) |
| `reminder_sent` | ✅ Persiste en PostgreSQL | Envío T-24hs | appointment_id, timestamp, channel |
| `reminder_response` | ✅ Persiste en PostgreSQL (fix C1) | Respuesta al recordatorio | response_type (confirmo/cancelo/cambio), timestamp |
| `conversation_closed` | ✅ Persiste en PostgreSQL | Cierre conversación | duration_seg, n_mensajes, n_fallbacks, resultado_final |

**Resumen:** 10/10 eventos instrumentados. Todos persisten en PostgreSQL vía `event_logger.log_event()`.
✅ **CSAT data flow unificado** — `csat_submitted` ahora escribe en `feedback` (fuente canónica) + `event` (trazabilidad).

---

## 📊 Métricas (50 total — chatbot-mvp-completion)

✅ **50 queries implementadas** en `metrics_queries.py`: 12 MVP + 38 extendidas (9 casos de uso C1-C9).
⚠️ Sin datos reales hasta que se ejecute `alembic upgrade head` y se deploie.

### Métricas MVP (12) — `GET /api/v1/admin/metrics`

| # | Métrica | Estado | Umbral de Alerta |
|---|---------|--------|-----------------|
| 1 | Tasa conversión inicio → turno | ✅ Query lista | < 20% |
| 2 | % turnos creados por bot | ✅ Query lista | < 40% |
| 3 | Tasa abandono por paso | ✅ Query lista | > 40% |
| 4 | Tasa fallback | ✅ Query lista | > 25% |
| 5 | Top 10 mensajes con fallback | ✅ Query lista | - |
| 6 | % turnos nocturnos (20-8hs) | ✅ Query lista | < 30% |
| 7 | Tasa resolución autónoma | ✅ Query lista | < 50% |
| 8 | Tasa cancelación | ✅ Query lista | > 20% |
| 9 | Tasa no-show | ✅ Query lista | > 15% |
| 10 | Confirmación recordatorio | ✅ Query lista | < 50% |
| 11 | Servicios más reservados | ✅ Query lista (JOIN real) | - |
| 12 | CSAT promedio | ✅ Fix aplicado — `csat_submitted` escribe en `feedback` + `event` | < 3.5/5 |

### Métricas Extendidas (38) — 9 Casos de Uso

| Caso | Métricas | Descripción | Optimizaciones |
|------|----------|-------------|----------------|
| C1 | E01–E04 | Conversión por servicio | Pre-fetch map (anti N+1) |
| C2 | E05–E08 | Efectividad de recordatorios | JOIN con reminder_log |
| C3 | E09–E12 | Sesiones largas (>30 min) | CTE + ROW_NUMBER |
| C4 | ES01–ES04 | Métricas agregadas por servicio | GROUP BY en BD |
| C5 | ES05–ES10 | Análisis temporal (días/horas pico) | Bulk fetch + avg modificación |
| C6 | ES11–ES14 | Cancelaciones / no-show | Razones top, % cancel diario |
| C7 | EN01–EN03 | Engagement (recurrentes, avg request) | GROUP BY + subquery |
| C8 | EN04–EN05 | Read receipt buckets | Pre-fetch + elif + malformed |
| C9 | EN06–EN09 | Retención avanzada | CTE + ROW_NUMBER, percentiles nativos |

### Umbrales Configurables ✅
- ✅ `GET/PUT /api/v1/admin/metric-thresholds` con Pydantic `ThresholdItem(BaseModel)`
- ✅ `metric_name`, `warning_value`, `critical_value`, `operator: Literal["lt","gt"]`
- ✅ Modelo `MetricThreshold` con `business_id` FK → multi-tenant

---

## 🎯 Próximos Pasos Recomendados (Actualizado 12 julio 2026)

### Prioridad 1 - Modelos SQLAlchemy ✅ COMPLETO (PR #58)
1. ~~Crear modelos SQLAlchemy completos~~
2. ~~Configurar Base metadata compartida en database.py~~
3. ~~Migrar a async engine~~ → postergado (el engine síncrono funciona)

### Prioridad 2 - Migrations + Servicios CRUD ✅ COMPLETO (PR #58)
1. ~~Crear initial migration Alembic~~ → modelos listos, falta ejecutar `revision --autogenerate`
2. ~~Implementar servicios CRUD~~ → catalog, calendar, negocio, faq implementados

### Prioridad 3 - Scheduler de Recordatorios ✅ COMPLETO (chatbot-mvp-completion)
1. ~~Implementar Celery/APScheduler para recordatorios T-24hs~~ → Celery Beat 9 AM
2. ~~Conectar con `send_message` de whatsapp.py~~ → 4 niveles de fallback
3. ~~Los eventos `reminder_sent` y `reminder_response` ya están instrumentados~~

### Prioridad 4 - Métricas y Eventos ✅ COMPLETO (chatbot-mvp-completion)
1. ~~Persistir eventos~~ → 10/10 eventos instrumentados con `log_event()`
2. ~~Implementar eventos faltantes~~ → CSAT unificado
3. ~~Unificar CSAT data flow~~ → `csat_submitted` escribe `feedback` + `event`
4. ~~Dashboard con métricas críticas~~ → 50 métricas, endpoint REST listo
5. ~~Umbrales configurables~~ → Pydantic ThresholdItem en `/api/v1/admin/metric-thresholds`

### Pendiente REAL (lo que falta para prod)
1. ⏳ **Ejecutar Alembic**: `docker compose up -d db redis` → `alembic revision --autogenerate` → `alembic upgrade head`
2. ⏳ **Crear volúmenes Docker**: `sudo mkdir -p /var/tmp/chatbot_postgres_data /var/tmp/chatbot_redis_data`
3. ⏳ **Verificación end-to-end**: levantar `docker compose up -d` completo y correr tests
4. ⏳ **Code Review Grade A**: 0 BLOCKER, 0 CRITICAL, 0 WARNING — listo para merge
5. ⏳ **PR #58 merge a develop** → review requerido (ver `.specify/features/chatbot-mvp-completion/review.md`)
6. ⏳ **Frontend dashboard**: endpoint REST de métricas listo, falta UI
7. ⏳ **Token WhatsApp real**: mock actual via `settings.WHATSAPP_TOKEN`

---

## 📂 Archivos Clave del Proyecto

### Backend (revisados y verificados):
- ✅ `backend/app/main.py` — Estructura de routers
- ✅ `backend/app/api/v1/chatbot/webhook.py` — State Router + 10 eventos instrumentados (PR #58)
- ✅ `backend/app/services/whatsapp.py` — WhatsApp integration
- ✅ `backend/app/services/state_manager.py` — Redis state management
- ✅ `backend/app/core/settings.py` — 19 variables de entorno
- ✅ `backend/app/core/security.py` — JWT + Google OAuth2
- ✅ `backend/app/db/database.py` — Engine síncrono con imports de modelos
- ✅ `backend/app/db/models/` — 12 modelos SQLAlchemy (PR #58 + chatbot-mvp-completion)
- ✅ `backend/app/services/catalog.py` — CRUD servicios/productos (PR #58)
- ✅ `backend/app/services/calendar.py` — CRUD turnos (PR #58)
- ✅ `backend/app/services/negocio.py` — Orquestación chatbot (PR #58)
- ✅ `backend/app/services/faq.py` — CRUD FAQs (PR #58)
- ✅ `backend/app/services/event_logger.py` — log_event() fire-and-forget (PR #58)
- ✅ `backend/app/services/metrics_queries.py` — **50 métricas** (12 MVP + 38 extendidas C1-C9, optimizadas anti-N+1)
- ✅ `backend/app/scheduler/config.py` — Celery app config (Redis broker)
- ✅ `backend/app/scheduler/tasks.py` — `send_reminders()` con 4 niveles de fallback
- ✅ `backend/app/api/v1/admin/metrics.py` — Endpoint `GET /api/v1/admin/metrics`
- ✅ `backend/app/api/v1/admin/metric_thresholds.py` — **NUEVO** GET/PUT umbrales con Pydantic ThresholdItem
- ✅ `backend/app/api/v1/admin/reminder_log.py` — **NUEVO** GET reminder log
- ✅ `backend/app/api/v1/admin/health.py` — **NUEVO** Health check endpoint
- ✅ `backend/app/db/models/metric_threshold.py` — **NUEVO** Umbrales warning/critical configurables
- ✅ `backend/app/db/models/reminder_log.py` — **NUEVO** Trazabilidad de recordatorios
- ✅ `backend/app/data_seed.py` — Seed data: 1 negocio, 8 servicios, 4 productos, 6 FAQs, 1 admin, 8 sesiones, ~50 eventos, 5 feedbacks
- ✅ `backend/requirements.txt` — Dependencias completas (celery, redis, flower incluidas)
- ✅ `backend/tests/test_metrics_queries_extended.py` — **NUEVO** 36 tests métricas extendidas
- ✅ `backend/tests/test_scheduler_tasks.py` — **NUEVO** 22 tests scheduler + fallback
- ✅ `backend/tests/test_metric_thresholds.py` — **NUEVO** 15 tests umbrales configurables
- ⏳ `backend/app/db/migrations/` — Configurado pero sin `revision --autogenerate` ejecutado

### Frontend (revisados y verificados):
- ✅ `frontend/src/auth.js` — NextAuth v5 + Google Provider
- ✅ `frontend/src/app/api/auth/[...nextauth]/route.js` — Auth handlers
- ✅ `frontend/src/components/auth/` — GoogleButton + LoginForm
- ✅ `frontend/src/components/landing-page/` — 5 secciones
- ✅ `frontend/src/components/layout/` — Navbar + Footer
- ✅ `frontend/src/lib/logger.js` — Pino logger
- ✅ `frontend/src/proxy.js` — API proxy
- ✅ `frontend/Dockerfile` — Node 22-alpine
- ✅ `.github/workflows/ci-cd.yml` — CI/CD pipeline

### Documentación (Data_Analyst):
- ✅ `Data_Analyst/Documentacion_de_proyecto.md` — 60+ métricas, 12 críticas, 3 escenarios
- ✅ `Data_Analyst/schema_db.md` — 12 modelos SQLAlchemy documentados
- ✅ `Data_Analyst/Detalles_pendientes.md` — Este archivo
- ✅ `Data_Analyst/diagrama_fullstack.mmd` — Diagrama Mermaid unificado v2.0
- ✅ `Data_Analyst/README.md` — Índice del directorio
- ✅ `docs/verificacion-dev.md` — **NUEVO** Guía de verificación para otro developer (9 pasos)
- ✅ `docs/deploy.md` — **NUEVO** Guía de deploy Docker Compose
- ✅ `docs/user-guide-metrics.md` — **NUEVO** Guía de uso de métricas y umbrales
- ✅ `.specify/features/chatbot-mvp-completion/review.md` — **Grade A**, 0 BLOCKER, 0 CRITICAL, 0 WARNING
- ✅ `.specify/features/chatbot-mvp-completion/docs/walkthrough.md` — Arquitectura, data flow, componentes
- ✅ `.specify/features/chatbot-mvp-completion/testing/validation.md` — 63 acceptance criteria

---

## 📌 Resumen de PRs Mergeados a Develop

| PR | Commit | Descripción | Estado en features/data-models |
|----|--------|-------------|-------------------------------|
| #40 | `0b80bca` | Endpoints REST principales | ✅ Sincronizado |
| #43 | `121415e` | Máquina de estados WhatsApp + Redis | ✅ Sincronizado |
| #46 | `ade4640` | Mensajes interactivos botones/listas | ✅ Sincronizado |
| #47 | `c74559f` | Flujo híbrido árbol decisión + placeholder IA | ✅ Sincronizado |
| #48 | `6924bc2` | Google OAuth2 frontend (NextAuth v5) | ❌ Pendiente sincronizar |
| #49 | `a623c5f` | Test integración auth | ❌ Pendiente sincronizar |
| #50 | `431823` | CI/CD + test integración auth | ❌ Pendiente sincronizar |
| #58 | `d8ff029` | **data-models-metrics**: 10 modelos, 6 servicios, 12 métricas, seed data, endpoint admin/metrics | 🟢 Abierto → develop |
| #58 | `(varios)` | **chatbot-mvp-completion**: +38 métricas extendidas (50 total), scheduler Celery, umbrales configurables, CSAT fix, 73 tests, Grade A review | 🟢 Abierto → develop |

---

**Última actualización:** 12 de julio 2026 (America/Buenos_Aires)
**Próxima acción recomendada:** Mergear PR #58 a develop → `docker compose up -d db redis` → `alembic revision --autogenerate && alembic upgrade head` → levantar stack completo