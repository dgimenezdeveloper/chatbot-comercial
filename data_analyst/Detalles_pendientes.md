# Detalles Pendientes - Exploración del Proyecto Chatbot Comercial

**Fecha:** 10 de julio 2026
**Estado:** Actualizado tras PR #58 (data-models-metrics) en features/data-models + fixes C1-C4/W8
**Rama actual:** features/data-models (PR #58 abierto → develop)
**Nota:** Prioridades 1 y 2 del plan original RESUELTAS en PR #58. Prioridades 3 y 4 siguen pendientes.

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

## ⚠️ Estructuras sin Implementar

### **Modelos de Datos (DB)** - `/backend/app/db/models/`
✅ **IMPLEMENTADO en PR #58.** 10 modelos SQLAlchemy completos:

| Archivo | Modelo | Features clave |
|---------|--------|----------------|
| `business.py` | Business | Raíz multi-tenant, slug único, config WhatsApp |
| `user.py` | User | Roles admin/operator/guest, UniqueConstraint(phone, business_id) |
| `service.py` | Service | Catálogo con categorías y precios, composite PK (id, business_id) |
| `product.py` | Product | Productos con stock y costo, índice parcial is_active |
| `appointment.py` | Appointment | Turnos con 3 enums (status, no_show, created_via), composite PK |
| `faq.py` | FAQ | Preguntas frecuentes categorizadas con orden |
| `events.py` | Event | Eventos con JSONB payload, GIN index, FK a session |
| `sessions.py` | ChatSession | Sesiones con métricas agregadas (n_messages, n_fallbacks) |
| `feedback.py` | Feedback | CSAT 1-5 con outcome de interacción |
| `turno_apuesta.py` | TurnoApuesta | Gamificación de apuestas diarias |

Todos con índices de rendimiento, docstrings en español, y `ondelete` consistente.

### **Services de Negocio** - `/backend/app/services/`
- ✅ `whatsapp.py` - Integración con WhatsApp (COMPLETO)
- ✅ `state_manager.py` - Redis State Manager (COMPLETO)
- ✅ `catalog.py` - CRUD servicios/productos con soft-delete + validación whitelist (PR #58)
- ✅ `calendar.py` - Gestión de turnos: crear, listar, cancelar, actualizar estado (PR #58)
- ✅ `negocio.py` - Orquestación conectada a DB: get_or_create_user, slots disponibles (PR #58)
- ✅ `faq.py` - CRUD FAQs con búsqueda ILIKE y categorías (PR #58)
- ✅ `event_logger.py` - log_event() fire-and-forget para 10 eventos (PR #58)
- ✅ `metrics_queries.py` - 12 métricas MVP con queries SQL aggregate + all_metrics() (PR #58)

### **Scheduler de Recordatorios**
- ❌ No existe scheduler (Celery/APScheduler)
- ✅ La lógica de envío de mensaje WhatsApp ya está implementada en whatsapp.py
- ✅ El webhook ahora instrumenta `reminder_sent` y `reminder_response` (fix C1, PR #58)
- ⚠️ Falta el scheduler que dispare los envíos automáticos T-24hs

### **Migrations Alembic**
- ❌ No se ejecutó `alembic revision --autogenerate` aún
- ✅ Alembic configurado (`alembic.ini`, `env.py`, `script.py.mako`)
- ✅ `database.py` importa todos los modelos a `Base.metadata` (PR #58)

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

### Caso de uso 1: Agendar turno nuevo ✅ Implementado en webhook
- ✅ State Router con 8 handlers
- ✅ Soporte para mensajes interactivos (botones/listas)
- ✅ Flujo híbrido árbol de decisión + placeholder IA
- ⚠️ Conectado a DB real (usa Redis para estado, pero no persiste turnos en PostgreSQL)
- ⚠️ Recordatorios T-24hs (solo placeholder)

### Caso de uso 2: Modificar turno existente ❌ No implementado
- ❌ Buscar turno por usuario
- ❌ Disponibilidad para re-agendar
- ❌ Confirmación del cambio

### Caso de uso 3: Cancelar turno ❌ No implementado
- ❌ Validar cancelación antes de fecha/hora
- ❌ Notificación al negocio

### Caso de uso 4: Recordatorio automático T-24hs ⚠️ Placeholder
- ✅ Lógica de envío de mensaje WhatsApp implementada
- ❌ Scheduler automático (Celery/APScheduler)
- ⚠️ Solo funciona dentro de ventana 24h de WhatsApp

### Caso de uso 5: Consultar disponibilidad sin agendar ❌ No implementado
- ❌ Mostrar slots disponibles por día/hora
- ❌ Filtrado por servicio

### Caso de uso 6: Consultar precios ❌ No implementado
- ❌ Debe venir de DB real

### Caso de uso 7: Consultar profesionales/empleados ❌ No implementado
- ❌ No existe modelo de profesionales aún

### Caso de uso 8: Interacción bot vs escalamiento ✅ Parcial
- ✅ Lógica de fallback implementada (FALLBACK_1 → FALLBACK_2 → HUMAN_ESCALATION)
- ✅ Escalamiento automático tras 2 fallbacks consecutivos
- ⚠️ Notificación al humano no implementada

---

## 📊 Infraestructura y DevOps

### Docker Compose ✅ Parcial
- ✅ Backend container (Python 3.11-slim, port 8000)
- ✅ PostgreSQL container (postgres:16-alpine, port 5432)
- ✅ Redis container (redis:7-alpine, port 6379)
- ✅ Frontend container (Node 22-alpine, port 3000) — NUEVO PR #48

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
⚠️ CSAT data flow: `csat_submitted` se guarda en tabla `event`, pero M12 (`get_csat_average()`) consulta `feedback`. Pendiente unificar.

---

## 📊 Métricas Críticas (12 MVP)

✅ **12 queries implementadas en PR #58** (`metrics_queries.py` + endpoint `GET /api/v1/admin/metrics`).
⚠️ Sin datos reales hasta que se ejecute `alembic upgrade head` y se deploie.

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
| 12 | CSAT promedio | ⚠️ Query lista pero lee `feedback`, no `event` | < 3.5/5 |

---

## 🎯 Próximos Pasos Recomendados (Actualizado 10 julio 2026)

### Prioridad 1 - Modelos SQLAlchemy ✅ COMPLETO (PR #58)
~~1. Crear modelos SQLAlchemy completos~~
~~2. Configurar Base metadata compartida en database.py~~
~~3. Migrar a async engine~~ → postergado (el engine síncrono funciona)

### Prioridad 2 - Migrations + Servicios CRUD ✅ COMPLETO (PR #58)
~~1. Crear initial migration Alembic~~ → modelos listos, falta ejecutar `revision --autogenerate`
~~2. Implementar servicios CRUD~~ → catalog, calendar, negocio, faq implementados

### Prioridad 3 - Scheduler de Recordatorios (Pendiente)
1. Implementar Celery/APScheduler para recordatorios T-24hs
2. Conectar con `send_message` de whatsapp.py (ya implementado)
3. Los eventos `reminder_sent` y `reminder_response` ya están instrumentados

### Prioridad 4 - Métricas y Eventos (Parcialmente completo)
1. ~~Persistir eventos~~ → ✅ 10/10 eventos instrumentados con `log_event()`
2. ~~Implementar eventos faltantes~~ → ✅ completos (fix C1)
3. Ejecutar `alembic upgrade head` para crear tablas en PostgreSQL
4. Dashboard con 12 métricas críticas → endpoint REST listo, falta frontend
5. Unificar CSAT data flow (`csat_submitted` en `event` vs M12 leyendo `feedback`)

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
- ✅ `backend/app/db/models/` — 10 modelos SQLAlchemy (PR #58)
- ✅ `backend/app/services/catalog.py` — CRUD servicios/productos (PR #58)
- ✅ `backend/app/services/calendar.py` — CRUD turnos (PR #58)
- ✅ `backend/app/services/negocio.py` — Orquestación chatbot (PR #58)
- ✅ `backend/app/services/faq.py` — CRUD FAQs (PR #58)
- ✅ `backend/app/services/event_logger.py` — log_event() fire-and-forget (PR #58)
- ✅ `backend/app/services/metrics_queries.py` — 12 métricas MVP (PR #58)
- ✅ `backend/app/api/v1/admin/metrics.py` — Endpoint GET /api/v1/admin/metrics (PR #58)
- ✅ `backend/app/data_seed.py` — Seed data: 1 negocio, 8 servicios, 4 productos, 6 FAQs, 1 admin, 8 sesiones, ~50 eventos, 5 feedbacks (PR #58)
- ✅ `backend/requirements.txt` — Dependencias completas
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
- ✅ `Data_Analyst/schema_db.md` — 10 modelos SQLAlchemy documentados
- ✅ `Data_Analyst/Detalles_pendientes.md` — Este archivo
- ✅ `Data_Analyst/diagrama_fullstack.mmd` — Diagrama Mermaid unificado v2.0
- ✅ `Data_Analyst/README.md` — Índice del directorio

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

---

**Última actualización:** 10 de julio 2026 (America/Buenos_Aires)
**Próxima acción recomendada:** Mergear PR #58 a develop → ejecutar `alembic revision --autogenerate` → scheduler recordatorios