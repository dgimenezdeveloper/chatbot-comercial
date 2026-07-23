# Chatbot Comercial — Wiki de Métricas y Analítica de Datos

> **Versión:** julio 2026 · **Para:** equipo de desarrollo y análisis

---

## 📊 Visión General

El sistema cuenta con **50 métricas implementadas** (12 críticas MVP + 38 extendidas en 9 casos de uso) que permiten medir el rendimiento del chatbot, la conversión de turnos, la satisfacción del cliente y el impacto en el negocio.

### Arquitectura de Datos

```
Conversaciones (WhatsApp/Web)
        │
        ▼
  event_logger.py (log_event fire-and-forget)
        │
        ▼
  PostgreSQL (tabla event + feedback + appointment + session)
        │
        ▼
  metrics_queries.py (50 queries SQL agregadas)
        │
        ▼
  GET /api/v1/admin/metrics (endpoint REST)
```

---

## 🎯 12 Métricas Críticas (MVP)

| # | Métrica | Cálculo | Umbral Alerta |
|---|---------|---------|---------------|
| 1 | Tasa conversión inicio → turno | `turnos_creados / conversations_iniciadas` | < 20% |
| 2 | % turnos creados por bot | `turnos_via_bot / total_turnos` | < 40% |
| 3 | Tasa abandono por paso | `usuarios_que_no_avanzan / usuarios_en_paso` | > 40% |
| 4 | Tasa fallback (NLU) | `fallbacks / total_mensajes` | > 25% |
| 5 | Top 10 mensajes con fallback | Ranking de intenciones no entendidas | Cualquier cambio |
| 6 | % turnos nocturnos (20-8hs) | `turnos_creados_20a8 / total_turnos` | < 30% |
| 7 | Tasa resolución autónoma | `(turnos + consultas_resueltas) / total` | < 50% |
| 8 | Tasa cancelación | `cancelados / total_turnos` | > 20% |
| 9 | Tasa no-show | `no_asistieron / total_turnos` | > 15% |
| 10 | Confirmación recordatorio | `confirmaciones / recordatorios_enviados` | < 50% |
| 11 | Servicios más reservados | Ranking por volumen | Accionable |
| 12 | CSAT promedio | Media de scores 1-5 post-conversación | < 3.5 |

---

## 📡 10 Eventos Instrumentados

Todos los eventos persisten en PostgreSQL vía `event_logger.log_event()` y están disponibles vía API.

| Evento | Momento | Payload clave |
|--------|---------|---------------|
| `conversation_started` | Primer mensaje del usuario | is_new_user, channel |
| `menu_option_selected` | Usuario elige opción | option_name |
| `service_selected` | Confirma servicio | service_id, confidence_score |
| `fallback_triggered` | Bot no entiende | message_original, fallback_n |
| `appointment_created` | Turno confirmado | via_bot, horario_nocturno |
| `escalation_to_human` | Escala a humano | reason, n_fallbacks_previos |
| `csat_submitted` | Usuario califica | score (1-5), outcome |
| `reminder_sent` | Envío T-24hs | appointment_id, channel |
| `reminder_response` | Respuesta recordatorio | response_type |
| `conversation_closed` | Cierre conversación | duracion_seg, n_mensajes, resultado_final |

---

## ⏰ Recordatorios Automáticos (Celery)

- **Schedule:** Una vez por día a las 9 AM (hora Buenos Aires) vía Celery Beat
- **Worker:** Celery Worker con Redis como broker
- **4 niveles de fallback:**
  1. Template pago de Meta (sin límite de 24h)
  2. WhatsApp normal (si el cliente escribió en las últimas 24h)
  3. Canal alternativo (SMS/email si configurado)
  4. Notificar al dueño por WhatsApp
- **Trazabilidad:** Cada intento se registra en `ReminderLog` con status/channel/error_reason

### Endpoints de recordatorios
```
GET  /api/v1/admin/reminder-log      # Historial de envíos
GET  /api/v1/admin/health            # Health check
```

---

## 🗄️ Modelos de Datos (12 tablas)

| Tabla | Propósito | Registros seed |
|-------|-----------|---------------|
| `business` | Negocios multi-tenant | 1 (Salon Demo Belén) |
| `user` | Usuarios (admin/operator/guest) | 1 admin |
| `service` | Catálogo de servicios | 8 servicios |
| `product` | Productos vendibles | 4 productos |
| `appointment` | Turnos agendados | 280 (enriched) |
| `faq` | Preguntas frecuentes | 6 FAQs |
| `event` | Eventos instrumentados | ~3271 (enriched) |
| `session` | Sesiones de conversación | 500 (enriched) |
| `feedback` | CSAT scores | 91 (enriched) |
| `reminder_log` | Trazabilidad recordatorios | 154 (enriched) |
| `metric_threshold` | Umbrales configurables | 13 defaults |
| `turno_apuesta` | Gamificación (apuestas) | - |

---

## 🎛️ Umbrales Configurables

Cada métrica tiene valores **warning** (amarillo) y **critical** (rojo) configurables por negocio:

```
GET  /api/v1/admin/metric-thresholds              # Listar umbrales
PUT  /api/v1/admin/metric-thresholds              # Actualizar umbrales
```

Ejemplo de threshold:
```json
{
  "metric_name": "conversion_rate",
  "warning_value": 0.20,
  "critical_value": 0.10,
  "operator": "lt"
}
```

---

## 🌱 Seed Data

### Básico (idempotente)
```bash
docker compose exec api python -m app.data_seed
```
Crea: 1 business, 1 admin, 8 servicios, 4 productos, 6 FAQs, 13 thresholds.

### Enriquecido (30 días de datos realistas, trunca transaccionales)
```bash
docker compose exec api python -m app.data_seed --enriched
```
Crea: 500 sesiones, ~3271 eventos, 280 turnos, 91 feedbacks, 154 reminder_logs.

---

## 🔌 Endpoints REST (Admin)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/admin/metrics` | GET | 50 métricas en tiempo real |
| `/api/v1/admin/metric-thresholds` | GET/PUT | Umbrales warning/critical |
| `/api/v1/admin/reminder-log` | GET | Historial de recordatorios |
| `/api/v1/admin/health` | GET | Health check |

---

## 📐 Diagrama de Arquitectura

Ver `repositorio/data_analyst/diagrama_fullstack.mmd` (Mermaid v2.1) para el diagrama completo del stack incluyendo:
- Frontend (Next.js 16)
- Backend (FastAPI + Celery)
- Base de datos (PostgreSQL + Redis)
- CI/CD (GitHub Actions)
- Eventos y métricas

---

*Documento generado para la wiki del proyecto. Actualizado al 23 de julio 2026.*