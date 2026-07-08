# Detalles Pendientes - Exploración del Proyecto Chatbot Comercial

**Fecha:** 8 de julio 2026
**Estado:** Actualizado tras merge de 9 PRs a develop (PRs #40-#50)
**Rama actual:** Feature/Data-initial (sincronizada con origin/develop hasta 4 PRs: #40, #43, #46, #47)

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
El directorio existe pero está vacío. Faltan modelos SQLAlchemy:

- ❌ `business.py` - Modelo Negocio (clientela del chatbot)
- ❌ `turno.py` - Modelo Turno/Appointment
- ❌ `servicio.py` - Modelo Servicio
- ❌ `producto.py` - Modelo Producto
- ❌ `usuario.py` - Modelo Usuario
- ❌ `faq.py` - Modelo FAQ
- ❌ `events.py` - Modelo Event (métricas)
- ❌ `sessions.py` - Modelo Session
- ❌ `feedback.py` - Modelo Feedback/CSAT
- ❌ `turno_apuesta.py` - Modelo Apuesta a Turnos

### **Services de Negocio** - `/backend/app/services/`
- ✅ `whatsapp.py` - Integración con WhatsApp (COMPLETO)
- ✅ `state_manager.py` - Redis State Manager (COMPLETO)
- ❌ `catalog.py` - CRUD para productos/servicios
- ❌ `calendar.py` - Gestión de turnos y disponibilidad
- ❌ `negocio.py` - Lógica de orquestación del chatbot conectada a DB
- ❌ `faq.py` - Servicio CRUD para FAQs

### **Scheduler de Recordatorios**
- ❌ No existe scheduler (Celery/APScheduler)
- ⚠️ La lógica de envío de mensaje WhatsApp ya está implementada en whatsapp.py
- ⚠️ El webhook tiene placeholder para recordatorios T-24hs

### **Migrations Alembic**
- ❌ No hay initial migration para las tablas base
- ✅ Alembic configurado (`alembic.ini`, `env.py`, `script.py.mako`)

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

| Evento | Estado | Momento de disparo | Campos necesarios |
|--------|--------|-------------------|------------------|
| `conversation_started` | ⚠️ Parcial (Redis) | Primer mensaje usuario | session_id, business_id, timestamp, channel, is_new_user |
| `menu_option_selected` | ⚠️ Parcial (Redis) | Usuario elige opción | session_id, option_name |
| `service_selected` | ⚠️ Parcial (Redis) | Confirma servicio | service_id, confidence_score |
| `fallback_triggered` | ⚠️ Parcial (Redis) | Bot no entiende | message_original, previous_state, fallback_n |
| `appointment_created` | ❌ Pendiente | Turno confirmado | appointment_id, via_bot=true, duration_flujo_seg, horario_nocturno |
| `escalation_to_human` | ⚠️ Parcial (Redis) | Escala a humano | reason, n_fallbacks_previos, current_flow_state |
| `csat_submitted` | ❌ Pendiente | Usuario califica | score 1-5, outcome (turno/escalado/abandonado) |
| `reminder_sent` | ❌ Pendiente | Envío T-24hs | appointment_id, timestamp, channel |
| `reminder_response` | ❌ Pendiente | Respuesta al recordatorio | response_type (confirmo/cancelo/cambio), timestamp |
| `conversation_closed` | ⚠️ Parcial (Redis) | Cierre conversación | duration_seg, n_mensajes, n_fallbacks, resultado_final |

**Resumen:** 5/10 eventos parcialmente instrumentados en Redis. 5/10 pendientes. Ninguno persiste en PostgreSQL.

---

## 📊 Métricas Críticas (12 MVP)

| # | Métrica | Estado | Umbral de Alerta |
|---|---------|--------|-----------------|
| 1 | Tasa conversión inicio → turno | ❌ Sin datos | < 20% |
| 2 | % turnos creados por bot | ❌ Sin datos | < 40% |
| 3 | Tasa abandono por paso | ❌ Sin datos | > 40% |
| 4 | Tasa fallback | ❌ Sin datos | > 25% |
| 5 | Top 10 mensajes con fallback | ❌ Sin datos | - |
| 6 | % turnos nocturnos (20-8hs) | ❌ Sin datos | < 30% |
| 7 | Tasa resolución autónoma | ❌ Sin datos | < 50% |
| 8 | Tasa cancelación | ❌ Sin datos | > 20% |
| 9 | Tasa no-show | ❌ Sin datos | > 15% |
| 10 | Confirmación recordatorio | ❌ Sin datos | < 50% |
| 11 | Servicios más reservados | ❌ Sin datos | - |
| 12 | CSAT promedio | ❌ Sin datos | < 3.5/5 |

---

## 🎯 Próximos Pasos Recomendados (Actualizado 8 julio 2026)

### Prioridad 1 - Modelos SQLAlchemy (Día 1-2)
1. Crear modelos SQLAlchemy completos:
   - `business.py`, `usuario.py`, `servicio.py`, `producto.py`, `turno.py`, `faq.py`, `events.py`, `sessions.py`, `feedback.py`, `turno_apuesta.py`
2. Configurar Base metadata compartida en database.py
3. Migrar a async engine (actualmente create_engine síncrono)

### Prioridad 2 - Migrations + Servicios CRUD (Días 3-4)
1. Crear initial migration Alembic para todas las tablas
2. Implementar servicios CRUD con SQLAlchemy ORM:
   - `catalog.py`, `calendar.py`, `negocio.py`, `faq.py`

### Prioridad 3 - Scheduler de Recordatorios (Día 5)
1. Implementar Celery/APScheduler para recordatorios T-24hs
2. Conectar con `send_message` de whatsapp.py (ya implementado)

### Prioridad 4 - Métricas y Eventos (Día 6+)
1. Persistir eventos de Redis a PostgreSQL
2. Implementar eventos faltantes (appointment_created, csat_submitted, reminder_sent, reminder_response)
3. Dashboard con 12 métricas críticas

---

## 📂 Archivos Clave del Proyecto

### Backend (revisados y verificados):
- ✅ `backend/app/main.py` — Estructura de routers
- ✅ `backend/app/api/v1/chatbot/webhook.py` — State Router + 8 handlers
- ✅ `backend/app/services/whatsapp.py` — WhatsApp integration
- ✅ `backend/app/services/state_manager.py` — Redis state management
- ✅ `backend/app/core/settings.py` — 19 variables de entorno
- ✅ `backend/app/core/security.py` — JWT + Google OAuth2
- ✅ `backend/app/db/database.py` — Engine síncrono (requiere async)
- ✅ `backend/requirements.txt` — Dependencias completas
- ⏳ `backend/app/db/models/` — VACÍO, requiere implementación
- ⏳ `backend/app/db/migrations/` — Configurado pero sin migraciones

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

| PR | Commit | Descripción | Estado en Feature/Data-initial |
|----|--------|-------------|-------------------------------|
| #40 | `0b80bca` | Endpoints REST principales | ✅ Sincronizado |
| #43 | `121415e` | Máquina de estados WhatsApp + Redis | ✅ Sincronizado |
| #46 | `ade4640` | Mensajes interactivos botones/listas | ✅ Sincronizado |
| #47 | `c74559f` | Flujo híbrido árbol decisión + placeholder IA | ✅ Sincronizado |
| #48 | `6924bc2` | Google OAuth2 frontend (NextAuth v5) | ❌ Pendiente sincronizar |
| #49 | `a623c5f` | Test integración auth | ❌ Pendiente sincronizar |
| #50 | `431823` | CI/CD + test integración auth | ❌ Pendiente sincronizar |

---

**Última actualización:** 8 de julio 2026, 6:30 PM (America/Buenos_Aires)
**Próxima acción recomendada:** Sincronizar Feature/Data-initial con origin/develop para incorporar PRs #48, #49, #50