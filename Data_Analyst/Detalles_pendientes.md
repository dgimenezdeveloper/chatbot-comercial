# Detalles Pendientes - Exploración del Proyecto Chatbot Comercial

**Fecha:** 5 de julio 2026  
**Estado:** Exploración inicial completada  

---

## 📁 Estructura Explorada del Backend

### **Backend API (FastAPI)** ✅ Completado

#### **Archivo: `/backend/app/main.py`**
- **Estado:** Implementado con endpoints mock
- **Routers activados:**
  - `/api/v1/auth` - Autenticación (login OAuth2)
  - `/api/v1/chatbot` - Chatbot (endpoint público con respuesta mock)
  - `/api/v1/catalog` - Productos/Servicios (protegido con JWT)
  - `/api/v1/faq` - Preguntas frecuentes (protegido con JWT)
  - `/api/v1/calendar` - Gestión de turnos (protegido con JWT)
  - `/api/v1/admin` - Panel administrativo (protegido con JWT)

#### **Archivo: `/backend/app/api/v1/chatbot/chat.py`**
- **Estado:** Endpoint básico con respuesta mock
- **Endpoint actual:** `POST /chat` → devuelve `"¡Hola! Recibí tu mensaje..."`

#### **Archivo: `/backend/app/schemas/faq.py`**
- **Estado:** Schemas Pydantic definidos
- **Classes:** `FAQRequest`, `FAQResponse` con campos: `pregunta`, `respuesta`, `id`

#### **Archivo: `/backend/app/api/v1/faq/router.py`**
- **Estado:** CRUD básico implementado
- **Endpoints:** GET, POST, PUT, DELETE para / (lista de FAQs hard-coded)

---

## ⚠️ Estructuras sin Implementar

### **Modelos de Datos (DB)** - `/backend/app/db/models/`
El directorio existe pero está vacío. Faltan modelos SQLAlchemy:

- ❌ `business.py` - Modelo Negocio (clientela del chatbot)
- ❌ `turno.py` - Modelo Turno/Apuesta
- ❌ `producto.py` - Modelo Producto
- ❌ `servicio.py` - Modelo Servicio
- ❌ `faq.py` - Modelo FAQ (aunque el schema ya existe)
- ❌ `usuario.py` - Modelo Usuario

### **Services de Negocio** - `/backend/app/services/`
Faltan servicios que conecten los endpoints con la base de datos:

- ❌ `catalog.py` - Servicios para productos/servicios
- ❌ `negocio.py` - Lógica de negocio del chatbot
- ❌ `faq.py` - Servicio CRUD para FAQs
- ❌ `calendar.py` - Gestión de turnos y disponibilidad
- ✅ `whatsapp.py` - Integración con WhatsApp (ya existe)

### **Schemas adicionales** - `/backend/app/schemas/`
Faltan schemas para:
- ❌ Negocio (Business)
- ❌ Turnos (Calendar)
- ❌ Productos/Servicios (Catalog)

---

## 📋 Checklist de Implementación Recomendado

### **Prioridad ALTA (MVP Básico)**

#### 1. Modelos SQLAlchemy - Crear DB schema
```
❌ database.py - Configurar conexión PostgreSQL (engine síncrono actual, no async)
❌ business.py - Negocio con campos: name, description, active
❌ turno.py - Turno con fecha/hora, negocio_id, status
❌ servicio.py - Servicio con duracion, precio, slots disponibles
❌ producto.py - Producto con stock, precio, imagen
❌ usuario.py - Usuario con rol (admin/cliente)
```

#### 2. Servicios de Negocio
```
❌ catalog.py - Listar/Crear productos y servicios
❌ negocio.py - Lógica del chatbot (rutas, fallback, escalada)
❌ faq.py - CRUD completo para preguntas frecuentes
❌ calendar.py - Gestión de turnos y disponibilidad
```

#### 3. Conectar Endpoints con DB
```
❌ chat/chat.py - Sustituir mock por llamada a DB
❌ faq/router.py - Usar servicio faq_service.FAQService
❌ catalog/productos.py - Implementar CRUD con SQLAlchemy
❌ catalog/servicios.py - Implementar CRUD con SQLAlchemy
❌ calendar/turnos.py - Implementar gestión de turnos
```

#### 4. Migrations Alembic
```
❌ Configurar versiones iniciales para todas las tablas
```

---

## 🎯 Funcionalidades del Chatbot (según Documentación)

### **Caso de uso 1: Agendar turno nuevo** ✅ Prioridad Crítica
- ✅ Tasa conversión inicio → turno
- ⚠️ Fallback handling
- ⚠️ Escalamiento a humano
- ⚠️ Recordatorios T-24hs

### **Caso de uso 2: Modificar turno existente** - No implementado
- ⚠️ Buscar turno por usuario
- ⚠️ Disponibilidad para re-agendar
- ⚠️ Confirmación del cambio

### **Caso de uso 3: Cancelar turno** - No implementado
- ⚠️ Validar cancelación antes de fecha/hora
- ⚠️ Notificación al negocio

### **Caso de uso 4: Recordatorio automático T-24hs** - No implementado
- ⚠️ Scheduler para disparar recordatorios
- ⚠️ Leer read receipts de WhatsApp

### **Caso de uso 5: Consultar disponibilidad sin agendar** - No implementado
- ⚠️ Mostrar slots disponibles por día/hora
- ⚠️ Filtrado por servicio

### **Caso de uso 6: Consultar precios** - Parcial (mock)
- ✅ Devuelve precio desde catálogo (hard-coded)
- ⚠️ Debe venir de DB real

### **Caso de uso 7: Consultar profesionales/empleados** - No implementado
- ❌ No existe modelo de profesionales aún

### **Caso de uso 8: Interacción bot vs escalamiento** - Parcial (mock)
- ⚠️ Lógica de fallback no implementada
- ⚠️ No hay orquestación de flujo

---

## 🔑 Eventos que el Backend debe Emitir (según métricas)

Estos eventos son cruciales para el dashboard de métricas:

| Evento | Momento de disparo | Campos necesarios |
|--------|-------------------|------------------|
| `conversation_started` | Primer mensaje usuario | session_id, business_id, timestamp, channel, is_new_user |
| `menu_option_selected` | Usuario elige opción | session_id, option_name |
| `service_selected` | Confirma servicio | service_id, confidence_score |
| `fallback_triggered` | Bot no entiende | message_original, previous_state, fallback_n |
| `appointment_created` | Turno confirmado | appointment_id, via_bot=true, duration_flujo_seg, horario_nocturno |
| `escalation_to_human` | Escala a humano | reason, n_fallbacks_previos, current_flow_state |
| `csat_submitted` | Usuario califica | score 1-5, outcome (turno/escalado/abandonado) |
| `reminder_sent` | Envío T-24hs | appointment_id, timestamp, channel |
| `reminder_response` | Respuesta al recordatorio | response_type (confirmo/cancelo/cambio), timestamp |

**Total: 10 eventos base para instrumentar el backend.**

---

## 📊 Métricas Críticas a Instrumentar

### **Métricas MVP (día 1):**
1. Tasa conversión inicio → turno (< 20% = alerta)
2. % turnos creados por bot (< 40% = alerta)
3. Tasa abandono por paso (> 40% = alerta)
4. Tasa fallback (> 25% = alerta)
5. Top 10 mensajes con fallback
6. % turnos nocturnos (20-8hs) (< 30% = sin valor agregado)
7. Tasa resolución autónoma (< 50% = necesita humano)
8. Tasa cancelación (> 20% = alerta)
9. Tasa no-show (> 15% = pérdida ingresos)
10. Confirmación recordatorio (< 50% = problema)
11. Servicios más reservados (ranking volumen)
12. CSAT promedio (< 3.5/5 = baja satisfacción)

### **Métricas de Engagement y Conversión:**
13. **Tasa respuesta inicial** (% usuarios que responden tras mensaje del bot) → Meta: >60%
14. **Tiempo medio respuesta usuario** (segundos desde último mensaje bot) → Meta: <2min
15. **Duración promedio sesión** (tiempo total en conversación activa) → Meta: 3-8 min
16. **Mensajes por sesión** (cantidad total de intercambios) → Meta: 8-15 mensajes
17. **Tasa retención D1/D7** (% usuarios que vuelven tras primer uso) → Meta: D1>25%, D7>10%
18. **Frecuencia de uso semanal** (sesiones/usuario/semana) → Meta: 2-4 sesiones
19. **Tasa completación flujo** (% que llegan al final sin abandonar) → Meta: >60%
20. **Puntos de fricción** (etapas con mayor abandono en funnel) → Identificar top 3
21. **Conversión por tipo de mensaje** (texto vs botón vs quick_reply) → Optimizar CTA
22. **Tasa interacción elementos UI** (% que tocan botones/menus) → Meta: >40%

### **Métricas de Negocio:**
23. **Ingreso promedio por turno** (valor monetario del servicio reservado)
24. **ROI chatbot** ((ingresos adicionales - costo operacion) / costo)
25. **Reducción tiempo reserva manual** (comparativo bot vs humano) → Meta: -70%
26. **Costo por conversación resuelta** (operación total / conversaciones completadas)
27. **Tasa upsell cross-sell** (% que agregan servicios adicionales al turno base)

### **Métricas de Calidad:**
28. **Precisión intent detection** (% correctamente identificados vs totales) → Meta: >85%
29. **Tiempo resolución problema** (desde inicio hasta solución confirmada) → Meta: <5min
30. **Tasa escalado exitoso** (% que tras escalamiento resuelven con humano) → Meta: >90%

---

## � Próximos Pasos Recomendados

### **Opción A: Implementar MVP Completo**
1. Crear modelos SQLAlchemy para todas las tablas
2. Implementar servicios de negocio con SQLAlchemy ORM
3. Conectar todos los endpoints con la DB real
4. Configurar Alembic migrations
5. Implementar lógica del chatbot con fallback y orquestación

### **Opción B: Priorizar Chatbot Primero**
1. Refactorizar `/chat/chat.py` con lógica de orquestación completa
2. Implementar fallback, intent detection, entity extraction
3. Crear modelos mínimos para negocio + turno
4. Agregar FAQs desde DB
5. Conectar con WhatsApp API real (webhook handler existente)

### **Opción C: Primero la Infraestructura**
1. Configurar DB schema completo primero
2. Implementar todos los CRUD de servicios
3. Luego integrar lógica del chatbot sobre esa infraestructura
4. Final: conectar webhook WhatsApp

---

## �� Preguntas para Decidir el Roadmap

1. **¿Qué base de datos se usará?** (PostgreSQL recomendado para producción, SQLite para desarrollo)
2. **¿Cuántos clientes/businesses soportar?** (multi-tenant desde inicio o uno por vez?)
3. **¿El chatbot es lineal o usa NLU/LLM?** (flujo predefinido vs inteligencia artificial)
4. **¿Recordatorio T-24hs es obligatorio desde MVP?** (impacta en WhatsApp Business API)
5. **¿Profesionales/empleados son necesarios desde el inicio?**

---

## 📂 Archivos Clave a Revisar

### **Ya revisados:**
- ✅ `backend/app/main.py` - Estructura de routers
- ✅ `backend/app/api/v1/chatbot/chat.py` - Endpoint chat actual (mock)
- ✅ `backend/app/schemas/faq.py` - Schemas Pydantic definidos
- ✅ `backend/app/api/v1/faq/router.py` - CRUD hard-coded

### **Por revisar:**
- ⏳ `backend/app/core/settings.py` - Configuración del app
- ⏳ `backend/app/core/security.py` - Implementación OAuth2/JWT
- ⏳ `backend/app/db/database.py` - Configuración de conexión DB
- ⏳ `backend/requirements.txt` - Dependencias actuales

---

## 📌 Notas Importantes

- **Estado actual:** Backend con endpoints funcionales pero todos usando datos hard-coded/mock
- **Próximo bloqueador:** Crear modelos SQLAlchemy antes de implementar servicios
- **Dependencia externa:** WhatsApp API (hay `whatsapp.py` en services - revisar implementación)
- **Multi-tenant:** La arquitectura parece soportar múltiples negocios desde el inicio

---

**Última actualización:** 5 de julio 2026, 4:02 PM  
**Próxima acción recomendada:** Crear modelos SQLAlchemy para la base de datos principal
