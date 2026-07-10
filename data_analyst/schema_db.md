# Schema Database — Chatbot Comercial

## 📋 Tabla de Contenido

1. [Visión General del Diseño DB](#-visión-general-del-diseño-db)
2. [Estrategia Multi-Tenant](#-estrategia-multi-tenant)
3. [Modelos SQLAlchemy Implementados](#-modelos-sqlalchemy-implementados)
4. [Modelos por Crear](#-modelos-por-crear)
5. [Relaciones y Foreign Keys](#-relaciones-y-foreign-keys)
6. [Eventos y Métricas](#-eventos-y-métricas)
7. [Índices Recomendados](#-índices-recomendados)
8. [Seed Data Inicial](#-seed-data-inicial)

---

## 📊 Visión General del Diseño DB

El sistema utiliza **PostgreSQL** como base de datos principal con arquitectura multi-tenant (cada cliente/biz tiene su propio espacio lógico mediante `business_id`).

### Stack Tecnológico
```yaml
Backend: Python 3.11+
ORM: SQLAlchemy 2.0.28
Async: FastAPI 0.110.0
Migrations: Alembic 1.13.1
Cache: Redis 7+ (sesiones, state management)

Frontend: Next.js 16.2.9 (App Router)
Auth: NextAuth v5 (beta) + Google OAuth2
UI: React 19.2.4, TailwindCSS 4, shadcn/ui 4.11.0
Logger: Pino

DevOps: Docker Compose (4 servicios), GitHub Actions CI/CD
```

### Estado Actual
- ✅ **Estructura de backend**: Routers y endpoints definidos, webhook funcional con State Router
- ✅ **WhatsApp Integration**: `services/whatsapp.py` completo (send_message, interactivos)
- ✅ **State Manager**: `services/state_manager.py` con Redis (get/set/clear user_state)
- ✅ **Webhook**: State Router con 8 handlers + mensajes interactivos + flujo híbrido árbol/IA
- ✅ **Google OAuth2**: Backend (JWT + Google verification) + Frontend (NextAuth v5)
- ✅ **Frontend**: Next.js 16 con landing page, auth components, dashboard, UI kit (10 componentes)
- ✅ **CI/CD**: GitHub Actions workflow (`.github/workflows/ci-cd.yml`)
- ✅ **Docker**: 4 servicios (API, Frontend, PostgreSQL, Redis)
- ⚠️ **Modelos SQLAlchemy**: `/backend/app/db/models/` está vacío
- ⚠️ **Schemas Pydantic**: Existen para auth/faq/chat/calendar/catalog/admin, falta conectar con DB
- ⚠️ **Services**: whatsapp.py y state_manager.py completos. Faltan catalog, calendar, negocio, faq

---

## 🏢 Estrategia Multi-Tenant

### Patrón: Foreign Keys + business_id

Todos los modelos de negocio incluyen `business_id` como foreign key hacia la tabla `business`:

```python
class BaseBusinessTable(Base):
    __abstract__ = True
    
    # ForeignKey con cascading deletes desde negocio
    business_id = Column(Integer, ForeignKey("business.id"), 
                        primary_key=True,  # Composite PK para aislamiento completo
                        nullable=False)
    
    class Config:
        cascade_delete_from_business = True  # Patrón custom
```

### Aislamiento de Datos
- Cada `business_id` tiene su propio conjunto de datos en todas las tablas
- Posibilidad de copias físicas futuras (tabla_x_biz_1, tabla_x_biz_2) si el volumen lo requiere
- Actual: Single schema con foreign keys + composite PK (recomendado para MVP)

---

## ✅ Modelos SQLAlchemy Implementados (Plano/Esquema)

### 1. `business` - Modelo Negocio

**Propósito**: Representa cada cliente del chatbot (peluquería, salon, etc.)

```python
class Business(Base):
    """Cliente principal del sistema"""
    
    __tablename__ = "business"
    
    id = Column(Integer, primary_key=True, index=True, description="ID interno")
    name = Column(String(200), nullable=False, 
                 description="Nombre del negocio (ej: 'Salon Belén')")
    slug = Column(String(100), unique=True, 
                  nullable=False, index=True, 
                  description="Slug para URLs /{slug}/dashboard")
    
    description = Column(Text, 
                        nullable=True, 
                        description="Descripción breve del negocio")
    
    # Estado
    active = Column(Boolean, default=True, 
                   description="Negocio activo en el sistema")
    
    # Configuración WhatsApp
    whatsapp_phone_id = Column(String(50), nullable=True,
                               description="WhatsApp Business Phone ID")
    whatsapp_business_account_id = Column(String(100), nullable=True,
                                         description="Business Account ID")
    whatsapp_verify_token = Column(String(100), nullable=True,
                                   description="Verify token para API")
    
    # Configuración adicional
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires",
                     description="Timezone del negocio")
    currency = Column(String(3), default="ARS", 
                     description="Moneda de precios")
    
    # Métodos de pago permitidos
    accept_cards = Column(Boolean, default=True,
                         description="Acepta tarjetas (para recordatorios)")
    accepts_cash = Column(Boolean, default=True,
                         description="Acepta efectivo")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        description="Fecha de creación")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                       description="Fecha de modificación")
```

**Campos Clave**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | Integer | ✅ | PK interno |
| name | String(200) | ✅ | Nombre negocio |
| slug | String(100) | ✅ | URL-friendly |
| description | Text | ❌ | Descripción breve |
| active | Boolean | ✅ | Estado activo |
| whatsapp_phone_id | String | ❌ | Phone ID WA |
| whatsapp_business_account_id | String | ❌ | Biz Account ID |
| timezone | String(50) | ❌ | Timezone |
| currency | String(3) | ❌ | Moneda |

---

### 2. `user` - Modelo Usuario

**Propósito**: Usuarios del sistema (dueños, operadores, guest)

```python
class User(Base):
    """Usuarios del negocio"""
    
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        primary_key=True,  # Composite PK
                        nullable=False)
    
    # Información personal
    name = Column(String(200), nullable=False,
                 description="Nombre completo")
    email = Column(String(255), unique=True, index=True,
                   nullable=True,
                   description="Email (para notificaciones)")
    phone = Column(String(20), unique=True, nullable=True,
                   description="WhatsApp personal")
    
    # Rol y acceso
    role = Column(Enum(['admin', 'operator', 'guest'], 
                       name="user_role"), 
                 default='guest',
                 description="Rol: admin=todo, operator=chatbot limitado, guest=read-only")
    
    is_active = Column(Boolean, default=True)
    
    # Autenticación
    password_hash = Column(String(256), nullable=True,
                          description="Hash para login (si aplica)")
    oauth_provider = Column(String(50), nullable=True,
                           description="Google, etc. (login social)")
    oauth_id = Column(String(100), unique=True, nullable=True,
                     description="ID de proveedor OAuth")
    
    # Permisos adicionales
    can_manage_appointments = Column(Boolean, default=False)
    can_view_analytics = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Campos Clave**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | Integer | ✅ | PK interno |
| business_id | Integer | ✅ | FK + PK composite |
| name | String(200) | ✅ | Nombre completo |
| email | String(255) | ❌ | Email (opcional) |
| phone | String(20) | ❌ | Teléfono/WhatsApp |
| role | Enum(admin,operator,guest) | ✅ | Rol de acceso |

---

### 3. `service` - Modelo Servicio

**Propósito**: Servicios disponibles para agendamiento (cortes, tintes, tratamientos)

```python
class Service(Base):
    """Servicios disponibles"""
    
    __tablename__ = "service"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        primary_key=True,
                        nullable=False)
    
    name = Column(String(200), nullable=False,
                 description="Nombre del servicio (ej: 'Corte de Cabello')")
    slug = Column(String(100), unique=True, nullable=False,
                 description="Slug para URLs")
    
    description = Column(Text, nullable=True,
                        description="Descripción detallada del servicio")
    
    # Categorización
    category = Column(Enum(['corte', 'coloración', 'tratamiento', 'barba', 
                           'otros'], name="service_category"), 
                     nullable=False,
                     description="Categoría principal")
    
    subcategory = Column(String(50), nullable=True,
                        description="Subcategoría (ej: 'Láser' para categorías)")
    
    # Precio y duración
    price = Column(Numeric(10, 2), default=0.00, nullable=False,
                  description="Precio en moneda del negocio")
    duration_minutes = Column(Integer, default=30, nullable=True,
                            description="Duración estimada (minutos)")
    
    # Disponibilidad
    slots_available_per_day = Column(Integer, default=8, nullable=True,
                                     description="Slots disponibles por día")
    is_active = Column(Boolean, default=True)
    
    # Stock si aplica
    requires_stock = Column(Boolean, default=False)
    stock_quantity = Column(Integer, nullable=True)
    
    # Imagenes
    image_url = Column(String(500), nullable=True,
                      description="URL de imagen del servicio")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Campos Clave**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | Integer | ✅ | PK interno |
| business_id | Integer | ✅ | FK + PK composite |
| name | String(200) | ✅ | Nombre servicio |
| category | Enum(corte,coloración,...) | ✅ | Categoría |
| price | Numeric(10,2) | ✅ | Precio |
| duration_minutes | Integer | ❌ | Duración (min) |

---

### 4. `product` - Modelo Producto

**Propósito**: Productos vendibles (productos de peluquería, accesorios)

```python
class Product(Base):
    """Productos disponibles"""
    
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        primary_key=True,
                        nullable=False)
    
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    
    description = Column(Text, nullable=True)
    
    # Precios
    price = Column(Numeric(10, 2), default=0.00, nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True,
                       description="Costo interno (para márgenes)")
    
    # Stock
    stock_quantity = Column(Integer, default=0, nullable=True)
    low_stock_threshold = Column(Integer, default=5,
                                description="Alerta de bajo stock")
    
    is_active = Column(Boolean, default=True)
    
    # Imagenes
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

### 5. `appointment` / `turno` - Modelo Turno

**Propósito**: Turnos agendados (principal M2P, futuro soporte de M2B para modificaciones)

```python
class Appointment(Base):
    """Turnos agendados"""
    
    __tablename__ = "appointment"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        primary_key=True,
                        nullable=False)
    
    # Relación con usuario (cliente)
    user_id = Column(Integer, ForeignKey("user.id"), 
                    nullable=True,  # Puede ser anónimo en chatbot directo
                    description="ID usuario si logueado, null para guest")
    user_phone = Column(String(20), nullable=True,
                       description="Teléfono del cliente (guest)")
    user_name = Column(String(200), nullable=True,
                      description="Nombre del cliente (guest)")
    
    # Servicio asociado
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False,
                       description="ID servicio seleccionado")
    
    # Fecha y hora
    scheduled_date = Column(DateTime(timezone=True), nullable=False,
                           description="Fecha y hora del turno")
    
    # Estado
    status = Column(Enum(['scheduled', 'confirmed', 'in_progress', 
                         'completed', 'cancelled'], name="appointment_status"),
                   default='scheduled',
                   description="Estado: scheduled=agendado, confirmed=confirmado, etc.")
    
    no_show_status = Column(Enum(['pending', 'confirmed_yes', 'confirmed_no', 'suggested_change'],
                                name="no_show_status"),
                          nullable=True,
                          description="Estado recordatorio T-24hs:")
    
    # Cancelación
    cancelled_reason = Column(String(500), nullable=True,
                             description="Motivo cancelación (si aplica)")
    cancellation_scheduled_date = Column(DateTime(timezone=True), nullable=True,
                                         description="Fecha de cancelación original")
    notification_sent_at = Column(DateTime(timezone=True), nullable=True,
                                 description="Cuando se envió notificación de cancelación")
    
    # Métodos y canales
    created_via = Column(Enum(['web', 'chatbot', 'api'], name="creation_channel"),
                        default='chatbot',
                        description="Crea vía: web/chatbot/api")
    session_id = Column(String(100), nullable=True,
                       description="Session ID de conversación")
    
    # Estado WhatsApp
    whatsapp_sent_at = Column(DateTime(timezone=True), nullable=True)
    whatsapp_read_at = Column(DateTime(timezone=True), nullable=True)
    whatsapp_response_type = Column(String(50), nullable=True,
                                   description="Respuesta al recordatorio (confirmó/canceló)")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Campos Clave**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | Integer | ✅ | PK interno |
| business_id | Integer | ✅ | FK + PK composite |
| user_phone | String(20) | ❌ | Teléfono cliente (guest) |
| user_name | String(200) | ❌ | Nombre cliente (guest) |
| service_id | Integer | ✅ | FK servicio |
| scheduled_date | DateTime | ✅ | Fecha/hora turno |
| status | Enum | ✅ | Estado del turno |
| no_show_status | Enum | ❌ | Estado recordatorio |

---

### 6. `turno_apuesta` - Modelo Apuesta a Turnos

**Propósito**: Apuestas diarias a cantidad de turnos (funcionalidad específica)

```python
class TurnoApuesta(Base):
    """Apuestas diarias"""
    
    __tablename__ = "turno_apuesta"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        primary_key=True,
                        nullable=False)
    
    # Relación turno
    appointment_id = Column(Integer, ForeignKey("appointment.id"), nullable=True,
                           description="ID turno relacionado (si aplica)")
    
    user_phone = Column(String(20), nullable=True,
                       description="Teléfono apostador")
    user_name = Column(String(200), nullable=True,
                      description="Nombre apostador")
    
    # Apuesta
    scheduled_date = Column(Date, nullable=False,
                           description="Fecha a apostar")
    estimated_turnos = Column(Integer, default=0)  # Estimado del negocio
    apuesta_amount = Column(Numeric(10, 2), default=0.00, nullable=False,
                           description="Monto apostado")
    
    status = Column(Enum(['open', 'settled'], name="apuesta_status"),
                   default='open',
                   description="open=pendiente, settled=resuelta")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

### 7. `faq` - Modelo FAQ

**Propósito**: Preguntas frecuentes del negocio

```python
class FAQ(Base):
    """Preguntas Frecuentes"""
    
    __tablename__ = "faq"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        nullable=False)
    
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    
    order = Column(Integer, default=0, nullable=True,
                  description="Orden de display")
    is_active = Column(Boolean, default=True)
    
    category = Column(String(100), nullable=True,
                     description="Categoría (ej: 'precios', 'turnos')")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

### 8. `events` - Tabla de Eventos (Métricas)

**Propósito**: Registro de eventos para instrumentar métricas en tiempo real

```python
class Event(Base):
    """Eventos para análisis y métricas"""
    
    __tablename__ = "event"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True,
                       description="Session ID único de conversación")
    business_id = Column(Integer, ForeignKey("business.id"), 
                        nullable=False,
                        index=True,
                        description="Cliente multi-tenant")
    
    # Tipo de evento (instrumentado)
    event_type = Column(String(100), nullable=False,
                       description="Tipo: conversation_started, menu_option_selected, etc.")
    
    # Payload JSON con todos los campos del evento
    payload_json = Column(JSONB, nullable=True,
                         description="JSON con todos los campos del evento")
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Métricas adicionales calculadas
    user_id = Column(Integer, ForeignKey("user.id"), 
                    nullable=True)  # Si usuario logueado
    
    channel = Column(Enum(['whatsapp', 'web'], name="event_channel"),
                    default='whatsapp')
```

**Eventos Instrumentados (10 Base)**:
| Evento | Campo Principal | Descriptivo de payload_json |
|--------|-----------------|----------------------------|
| `conversation_started` | is_new_user | Usuario nuevo/sesión nueva + channel |
| `menu_option_selected` | option_name | Opción seleccionada + confianza |
| `service_selected` | service_id, total_price | Servicio y precio |
| `fallback_triggered` | message_original, fallback_n | Mensaje original + intento de fallback |
| `appointment_created` | appointment_id, horario_nocturno | Turno creado + flag nocturno |
| `escalation_to_human` | reason, n_fallbacks_previos | Motivo escalamiento + fallbacks previos |
| `csat_submitted` | score (1-5), outcome | Score y resultado final |
| `reminder_sent` | appointment_id, timestamp | Recordatorio enviado + hora |
| `reminder_response` | response_type, timestamp | Respuesta al recordatorio |
| `conversation_closed` | duration_seg, n_mensajes, resultado_final | Cierre de conversación con métricas |

---

### 9. `sessions` - Tabla de Sesiones

**Propósito**: Rastreo de sesiones de conversación (para analytics detallados)

```python
class Session(Base):
    """Sesiones de conversación"""
    
    __tablename__ = "session"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        nullable=False)
    
    session_id = Column(String(100), unique=True, index=True,
                       description="Session ID WhatsApp")
    
    # Usuario asociado (si logueado)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user_phone = Column(String(20), nullable=True)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estado
    status = Column(Enum(['active', 'completed', 'abandoned'], name="session_status"),
                   default='active')
    
    # Métricas de sesión
    n_messages_total = Column(Integer, default=0)
    n_fallbacks = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

### 10. `feedback` - Tabla de Feedback/CSAT

**Propósito**: Calificaciones de satisfacción del usuario

```python
class Feedback(Base):
    """Feedback/CSAT"""
    
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"), 
                        nullable=False)
    
    session_id = Column(String(100), nullable=False,
                       description="Session ID de la conversación")
    
    score = Column(Integer, nullable=False, 
                  description="Score 1-5")
    
    comment = Column(String(1000), nullable=True)
    
    outcome = Column(Enum(['turno_exitoso', 'escalado_exitoso', 
                         'abandonado', 'fallback_malicioso'], name="feedback_outcome"),
                    description="Resultado de la interacción")
    
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_phone = Column(String(20), nullable=True)  # Para guest
```

---

## ⚠️ Modelos por Crear (Pendientes de Implementación)

### Lista Completa a Crear:

1. **`business.py`** - Tabla `Business` (✅ Esquema definido arriba)
2. **`user.py`** - Tabla `User` (✅ Esquema definido arriba)  
3. **`service.py`** - Tabla `Service` (✅ Esquema definido arriba)
4. **`product.py`** - Tabla `Product` (✅ Esquema definido arriba)
5. **`appointment.py`** - Tabla `Appointment` (✅ Esquema definido arriba)
6. **`turno_apuesta.py`** - Tabla `TurnoApuesta` (✅ Esquema definido arriba)
7. **`faq.py`** - Tabla `FAQ` (✅ Esquema definido arriba)
8. **`events.py`** - Tabla `Event` (✅ Esquema definido arriba)
9. **`sessions.py`** - Tabla `Session` (✅ Esquema definido arriba)
10. **`feedback.py`** - Tabla `Feedback` (✅ Esquema definido arriba)

### Modelos Faltantes Adicionales:

- **`message_log.py`** - Registro completo de mensajes (WhatsApp + bot) para debugging y analytics detallados
- **`notifications.py`** - Cola de notificaciones pendientes de enviar
- **`templates.py`** - Plantillas WhatsApp personalizadas por negocio

---

## 🔗 Relaciones y Foreign Keys

### Diagrama de Relaciones:

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│    business     │──────│              │      │                │
│   (PK: id)      │  FK +│    user      │  FK  │                │
│                 │ PK+──│  (PK: id,   │  FK + │        service  │
├─────────────────┤     └──────┬────────┘      │   (PK: id)      │
│ name            │           │               │                 │
│ whatsapp...     │    foreign_key│             │ business_id    │
│ active          │           │               │                 │
└────────┬────────┘           │               │  price, duration │
         │                    │   appointment │                 │
         │                  ┌──┴──────┐       │ (PK: id)        │
         │                  │         │      │ business_id     │
         │                  │ turnos  │ FK    │ user_id (opt)   │
         │                  │(FK + PK)│       │ service_id      │
         │                  └────┬────┘      │ scheduled_date  │
         │                       │           │ status           │
         │          ┌────────────▼─────────┐ │ no_show_status   │
         │          │                     │ │ created_at        │
         │          │    events           │ │ updated_at        │
         │          │   (PK: id)          │ │                    │
         │          │ session_id + FK     │ │ (FKs a business)  │
         │          └─────────────────────┘ │ timestamp, payload │
         │                                  │ JSONB              │
         │                     ┌────────────▼─────────┐           │
         │                     │                       │          │
         │                     │    notifications     │          │
         │                     │  (cola pendientes)   │          │
         │                     └─────────────────────┘          │
         │                                                       │
         └──────────────────→ feedback → FKs a business+session  │
```

### Foreign Keys con Cascading:

| Tabla | Columna | Referencia | Action on Delete |
|-------|---------|------------|------------------|
| service | business_id | business(id) | CASCADE (borra servicios del negocio borrado) |
| product | business_id | business(id) | CASCADE |
| appointment | business_id | business(id) | CASCADE |
| appointment | user_id | user(id) | SET NULL (cliente puede cambiar de user si necesario) |
| appointment | service_id | service(id) | RESTRICT (no borrar servicio con turnos activos) |

---

## 📊 Eventos y Métricas

### 12 Métricas Críticas del MVP:

| # | Métrica | Umbral Alerta | Descripción |
|---|---------|---------------|-------------|
| 1 | Tasa conversión inicio → turno | < 20% = alerta | % usuarios que llegan a crear turno |
| 2 | % turnos creados por bot | < 40% = alerta | Autonomía del bot vs humano |
| 3 | Tasa abandono por paso | > 40% = alerta | Drop-off en funnel de conversión |
| 4 | Tasa fallback | > 25% = alerta | % mensajes no entendidos |
| 5 | Top 10 mensajes con fallback | - | Para agregar nuevas intenciones |
| 6 | % turnos nocturnos (20-8hs) | < 30% = sin valor agregado | Valor agregado horario |
| 7 | Tasa resolución autónoma | < 50% = necesita humano | Auto-resolución vs escalamiento |
| 8 | Tasa cancelación | > 20% = alerta | Cancelaciones totales |
| 9 | Tasa no-show | > 15% = pérdida ingresos | Faltas a turnos confirmados |
| 10 | Confirmación recordatorio | < 50% = problema | % usuarios confirman recordatorio |
| 11 | Servicios más reservados | - | Ranking por volumen |
| 12 | CSAT promedio | < 3.5/5 = baja satisfacción | Puntuación media de feedback |

### Eventos Instrumentados (10 Base):

| Evento | Trigger | Payload Clave |
|--------|---------|---------------|
| `conversation_started` | Primer mensaje usuario | `{is_new_user, channel, session_id}` |
| `menu_option_selected` | Usuario elige opción | `{option_name, confidence_score}` |
| `service_selected` | Confirma servicio | `{service_id, total_price, quantity}` |
| `fallback_triggered` | Bot no entiende | `{message_original, previous_state, fallback_n}` |
| `appointment_created` | Turno confirmado | `{appointment_id, via_bot, duration_flujo_seg, horario_nocturno}` |
| `escalation_to_human` | Escala a humano | `{reason, n_fallbacks_previos, current_flow_state}` |
| `csat_submitted` | Usuario califica | `{score (1-5), outcome (turno/escalado/abandonado)}` |
| `reminder_sent` | Envío T-24hs | `{appointment_id, business_id, timestamp, channel}` |
| `reminder_response` | Respuesta al recordatorio | `{appointment_id, response_type, timestamp}` |
| `conversation_closed` | Cierre conversación | `{session_id, duration_seg, n_mensajes, n_fallbacks, resultado_final}` |

---

## 🗂️ Índices Recomendados

### Índices B-tree (Por defecto):

```sql
-- business
CREATE INDEX idx_business_name ON business(name);

-- user  
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_phone ON user(phone);
CREATE INDEX idx_user_role ON user(role);

-- service/product
CREATE INDEX idx_service_category ON service(category);
CREATE INDEX idx_product_active ON product(is_active) WHERE is_active = true;

-- appointment (CRÍTICO para consultas frecuentes)
CREATE INDEX idx_appointment_status ON appointment(status) WHERE status IN ('scheduled', 'confirmed');
CREATE INDEX idx_appointment_date ON appointment(scheduled_date) WHERE status IN ('scheduled', 'confirmed');
CREATE INDEX idx_appointment_business_date ON appointment(business_id, scheduled_date) 
    WHERE status IN ('scheduled', 'confirmed');

-- events (CRÍTICO para analytics)
CREATE INDEX idx_event_type_timestamp ON event(event_type, timestamp);
CREATE INDEX idx_event_session ON event(session_id);
CREATE INDEX idx_event_business ON event(business_id);
CREATE INDEX idx_event_user ON event(user_id);

-- sessions  
CREATE INDEX idx_session_started ON session(started_at);
CREATE INDEX idx_session_status ON session(status) WHERE status = 'active';
```

### Índices GIN (para JSONB):

```sql
-- events payload_json
CREATE INDEX idx_event_payload ON event USING GIN(payload_json jsonb_path_ops);
```

---

## 🌱 Seed Data Inicial

### Datos por Cargar Inicialmente:

1. **Businesses** - Ejemplo inicial con 1-2 negocios de prueba
2. **Services/Productos** - Catálogo por negocio (ej: 10 servicios + 5 productos)
3. **FAQs** - Preguntas frecuentes comunes por tipo de negocio
4. **Usuarios Admin** - Usuarios de administración para cada negocio

### Script de Seed Sugerido:

```python
# backend/app/data_seed.py
async def seed_business():
    """Crear data inicial de negocios"""
    business = Business(
        name="Salon Demo Belén",
        slug="salon-demo-belen",
        description="Peluquería de ejemplo para pruebas",
        active=True,
        whatsapp_phone_id="PHONE_ID_DEMO",
        timezone="America/Argentina/Buenos_Aires",
        currency="ARS"
    )
    
async def seed_services(business_id):
    """Crear catálogo inicial de servicios"""
    services = [
        Service(name="Corte Cabello", category="corte", price=5000, duration_minutes=30),
        Service(name="Tinte Raíz", category="coloración", price=8000, duration_minutes=60),
        # ... etc
    ]
    
async def seed_faqs(business_id):
    """Crear FAQs comunes"""
    faqs = [
        FAQ(question="¿Cómo agendo un turno?", answer="Escribí 'Sacar turno' y seguí el flujo..."),
        FAQ(question="¿Cuál es la política de cancelación?", answer="Podés cancelar con 24hs de anticipación...")
    ]
```

---

## 📌 Consideraciones Adicionales

### WhatsApp Business API Constraints:

1. **Ventana de mensajes**: Recordatorio T-24hs debe ser dentro de ventana gratuita (24h desde primer mensaje) o usar SMS alternativo
2. **Interactivos limitados**: Máximo 5 botones a la vez, lista con max 10 items
3. **Read receipts**: No todos los mensajes tienen confirmación de lectura

### Recordatorio T-24hs - Lógica Crítica:

```python
async def send_reminder(appointment: Appointment):
    """
    Disparador: 24 horas antes del scheduled_date
    Envía recordatorio automático + registra evento
    """
    message = f"""Hola {appointment.user_name},
      
Tu turno está confirmado para:
📅 {appointment.formatted_date}
⏰ {appointment.formatted_time}
💇 {appointment.service_name} - ${appointment.price}

¿Confirmas asistencia? Responde SI/NO

Podés cancelar escribiendo: cancelar"""
    
    # Enviar mensaje vía WhatsApp Business API
    await whatsapp.send(appointment.user_phone, message)
    
    # Registrar evento
    await db.record_event("reminder_sent", {
        "session_id": appointment.session_id,
        "appointment_id": str(appointment.id),
        "timestamp": datetime.utcnow()
    })
```

### Fallback Handling Strategy:

```
Intento 1 (Fallback 0): Bot responde según intención detectada
↓ (no entendido)
Intento 2 (Fallback 1): Ofrecer opciones alternativas
↓ (segundo error)  
Intento 3 (Fallback 2): Escalar automáticamente a humano → escalation_to_human event
```

### Multi-tenant Scaling Considerations:

| Estrategia | Cuándo Usar | Pros | Contras |
|------------|-------------|------|---------|
| **Foreign Keys + business_id** (Actual) | MVP y crecimiento moderado | Simple, SQL eficiente, consultas fáciles | JOINs necesarios |
| **Tablas separadas por biz** (ej: appointments_biz_1) | Alto volumen específico por cliente | Sin JOINs, aislamiento físico total | Múltiples queries a DB, más complejo |

---

## 📝 Notas de Implementación

### Orden Recomendado de Creación:

1. **database.py** - Configurar async engine + Base metadata compartido
2. **business.py + user.py** - Modelos multi-tenant base primero
3. **service.py + product.py** - Catálogo del negocio
4. **appointment.py** - Turnos (depende de service)
5. **faq.py** - FAQs por negocio
6. **events.py + sessions.py + feedback.py** - Analytics y métricas
7. **turno_apuesta.py** - Funcionalidad específica
8. **Inicial migration Alembic** - Crear initial migration para todas tablas

### Archivos SQLAlchemy:

```
backend/app/db/models/
├── __init__.py          # Importar todos los modelos
├── business.py          # Business, User (relación)
├── service.py           # Service
├── product.py           # Product  
├── appointment.py       # Appointment (turnos)
├── turno_apuesta.py     # TurnoApuesta
├── faq.py               # FAQ
├── events.py            # Event + Session + Feedback (analytics)
└── notifications.py     # Notifications (cola pendiente)
```

---

*Última actualización: 8 de julio 2026, 6:30 PM (America/Buenos_Aires)* — Refleja PRs #48, #49, #50 (Google OAuth2 frontend, CI/CD, tests integración)
