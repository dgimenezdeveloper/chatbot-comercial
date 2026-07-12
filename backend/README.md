
# Chatbot Comercial Backend 🚀

Backend dockerizado para el Chatbot Comercial, desarrollado con FastAPI, PostgreSQL y Redis.

## 📋 Índice

- [🛠️ Tecnologías](#️-tecnologías)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [⚙️ Configuración del Entorno (Onboarding)](#️-configuración-del-entorno-onboarding)
- [🗺️ Árbol de Rutas HTTP (API v1)](#️-árbol-de-rutas-http-api-v1)
- [🛠️ Swagger UI](#️-swagger-ui)
- [🌐 Integración con WhatsApp (Desarrollo Local)](#-integración-con-whatsapp-desarrollo-local)
- [📝 Notas Técnicas y Solución de Problemas](#-notas-técnicas-y-solución-de-problemas)
- [💻 Consideraciones de Entorno y Multiplataforma](#-consideraciones-de-entorno-y-multiplataforma)
- [🛑 Detener Servicios](#-detener-servicios)

---

## 🛠️ Tecnologías

- **Python**: 3.11-slim
- **FastAPI**: Framework web de alto rendimiento.
- **PostgreSQL**: Base de datos relacional (v16).
- **Redis**: Almacenamiento en memoria para caché y estados (v7).
- **SQLAlchemy**: ORM para interactuar con la base de datos.
- **Alembic**: Gestión de migraciones de base de datos.
- **Docker & Docker Compose**: Entorno de desarrollo aislado.

## 📁 Estructura del Proyecto

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── admin/        # Endpoints del panel del emprendedor
│   │   │   ├── chatbot/      # Endpoints y Webhooks de WhatsApp
│   │   │   ├── catalog/      # Gestión de productos/servicios
│   │   │   ├── faq/          # Preguntas frecuentes
│   │   │   ├── calendar/     # Integración con Google Calendar
│   │   │   └── auth/         # Autenticación JWT y OAuth
│   ├── core/                 # Configuración, seguridad y settings (Pydantic)
│   ├── db/                   # Modelos SQLAlchemy, sesiones y migraciones
│   ├── services/             # Lógica de negocio y clientes de API externas
│   ├── mcp/                  # Cliente Model Context Protocol
│   ├── schemas/              # Modelos Pydantic (Request/Response)
│   └── main.py               # Punto de entrada de la aplicación
├── tests/                    # Pruebas unitarias y de integración
├── requirements.txt          # Dependencias de Python
└── Dockerfile                # Receta de la imagen Docker
```

## ⚙️ Configuración del Entorno (Onboarding)

### 1. Clonar el repositorio
```bash
git clone <repo-url> && cd chatbot-comercial/backend
```

### 2. Crear .env local
Copia el archivo de ejemplo y ajusta las variables. **Importante:** Solicita las credenciales de Meta a los administradores o sigue la guía de WhatsApp más abajo.
```bash
cp .env.example .env
```

### 3. Levantar servicios con Docker
```bash
docker compose up --build
```

### 4. Verificar funcionamiento
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🗺️ Árbol de Rutas HTTP (API v1)

Este documento describe la estructura de rutas REST expuestas por el backend de la aplicación. La API está construida con **FastAPI** y se divide en dos grandes contextos: **Cliente Final (Chatbot)** y **Panel Administrativo (Emprendedor)**.

### 🤖 Chatbot (Cliente Final)
Rutas públicas utilizadas para la interacción con el usuario final a través de WhatsApp.

* `GET  /api/v1/chatbot/webhook` - Verificación técnica de Meta (Handshake).
* `POST /api/v1/chatbot/webhook` - Recepción de eventos y mensajes en tiempo real desde Meta WABA.
* `POST /api/v1/chatbot/chat` - Endpoint para procesar mensajes del cliente final (Mock inicial).

---

### 🔒 Panel Administrativo (Emprendedor)
*Todas las rutas a continuación requieren autenticación mediante el header `Authorization: Bearer <token>`.*

#### 📦 Catálogo (Catalog)
Gestión de los servicios y productos ofrecidos por el negocio.

**Servicios:**
* `GET    /api/v1/catalog/servicios/` - Lista todos los servicios.
* `POST   /api/v1/catalog/servicios/` - Crea un nuevo servicio.
* `PUT    /api/v1/catalog/servicios/{id}` - Actualiza un servicio existente.
* `DELETE /api/v1/catalog/servicios/{id}` - Elimina un servicio.

**Productos:**
* `GET    /api/v1/catalog/productos/` - Lista todos los productos.
* `POST   /api/v1/catalog/productos/` - Crea un nuevo producto.
* `PUT    /api/v1/catalog/productos/{id}` - Actualiza un producto existente.
* `DELETE /api/v1/catalog/productos/{id}` - Elimina un producto.

#### 📅 Agenda (Calendar)
Gestión de reservas y turnos.

* `GET    /api/v1/calendar/turnos/` - Lista todos los turnos agendados.
* `POST   /api/v1/calendar/turnos/` - Crea un nuevo turno.
* `DELETE /api/v1/calendar/turnos/{id}` - Cancela/Elimina un turno.

#### ❓ Preguntas Frecuentes (FAQ)
Gestión de la base de conocimiento del chatbot.

* `GET    /api/v1/faq/` - Lista todas las preguntas frecuentes.
* `POST   /api/v1/faq/` - Crea una nueva pregunta frecuente.
* `PUT    /api/v1/faq/{id}` - Actualiza una pregunta frecuente.
* `DELETE /api/v1/faq/{id}` - Elimina una pregunta frecuente.

#### ⚙️ Configuración del Negocio (Admin)
Gestión de los datos generales del local.

* `GET    /api/v1/admin/negocio/` - Obtiene la configuración actual del negocio.
* `PUT    /api/v1/admin/negocio/` - Actualiza la configuración del negocio.

---

## 🛠️ Swagger UI
Puedes probar e interactuar con todos estos endpoints directamente desde la documentación autogenerada por FastAPI ingresando a:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🌐 Integración con WhatsApp (Desarrollo Local)

Para que Meta (Facebook) pueda enviar mensajes a tu computadora local, necesitamos un túnel seguro con **ngrok**.

### 1. Configurar el túnel ngrok
1. Inicia sesión en [ngrok dashboard](https://dashboard.ngrok.com).
2. Obtén tu `Authtoken` y agrégalo a tu `.env` como `NGROK_AUTHTOKEN`.
3. Levanta el túnel apuntando al puerto de la API (8000):
   ```bash
   ngrok http 8000
   ```
4. Copia la URL generada (ej: `https://abcd-123.ngrok-free.app`).

### 2. Configurar el Webhook en Meta Developers
En el panel de tu App en [Meta for Developers](https://developers.facebook.com/apps/):
1. Ve a **WhatsApp > Configuración**.
2. En **Webhook**, haz clic en "Editar":
   - **URL de devolución de llamada**: `https://<tu-url-ngrok>/api/v1/chatbot/webhook`
   - **Token de verificación**: El valor de `WHATSAPP_VERIFY_TOKEN` en tu `.env`.
3. Haz clic en **"Verificar y guardar"**.
4. **IMPORTANTE:** En la tabla de campos, busca **`messages`** y haz clic en **Suscribirse**. Sin esto, no recibirás mensajes.

### 3. Abrir la ventana de 24 horas
WhatsApp solo permite que el bot responda si el usuario inició la conversación o si envías una plantilla aprobada.
- **Opción A:** Envía un mensaje de prueba ("Hello World") desde el panel de Meta a tu número.
- **Opción B:** Escribe "Hola" directamente al número de Sandbox desde tu celular.

---

## 📝 Notas Técnicas y Solución de Problemas

### 🇦🇷 Manejo de numeración (Argentina Sandbox)
Existe una discrepancia conocida en el **Sandbox de Meta** para números de Argentina:
- El Webhook recibe los mensajes con el formato `54 9 11 ...` (formato móvil internacional).
- El Sandbox a menudo solo permite responder si se usa el formato `54 11 5 ...` o quitando el `9`.

**Solución Implementada:**
En `app/api/v1/chatbot/webhook.py` existe una lógica de sanitización dinámica que detecta si el entorno es `development` y ajusta el prefijo automáticamente. 
> ⚠️ **Nota:** Esta lógica se desactiva en `production` para no interferir con la numeración real de la API de producción.

### 🔑 Token Permanente vs Temporal
- **No utilices** el token que aparece en la pantalla "Configuración de la API" de Meta, ya que expira en 24 horas.
- **Utiliza** el Token de **Usuario del Sistema** generado en el Business Manager con permisos `whatsapp_business_messaging`. Este token es permanente y debe ir en `WHATSAPP_TOKEN`.

---

## 💻 Consideraciones de Entorno y Multiplataforma

### VS Code Dev Containers (Recomendado)
El proyecto incluye soporte nativo. Al abrir la carpeta, VS Code detectará el entorno. Selecciona **"Reopen in Container"** para tener todas las herramientas configuradas automáticamente.

### Usuarios de Windows (WSL 2)
Es **indispensable** usar WSL 2. Si no usas Dev Containers, clona el repositorio dentro del sistema de archivos de Linux (ej: `\\wsl$\Ubuntu\home\user\...`) para que la recarga automática de Uvicorn (`--reload`) funcione correctamente.

---

## 🛑 Detener Servicios

Para detener los contenedores manteniendo los datos:
```bash
docker compose down
```

Para limpiar todo (incluyendo base de datos y volúmenes):
```bash
docker compose down -v
```