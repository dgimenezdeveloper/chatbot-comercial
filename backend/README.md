# Backend — Python API 🐍

Backend desarrollado en Python siguiendo una arquitectura simple y escalable.

## 🚀 Tecnologías

- **Python** 3.11+
- **FastAPI** / Flask (según implementación)
- **PostgreSQL** / MySQL
- **SQLAlchemy**
- **Docker**
- **JWT Authentication**

> Ver en wiki para más detalles sobre la arquitectura y decisiones técnicas [Stack Técnico](https://github.com/dgimenezdeveloper/chatbot-comercial/wiki/Stack-T%C3%A9cnico)

## 📁 Estructura del Proyecto

```bash
backend/
├─ app/
│  ├─ api/
│  │  ├─ v1/
│  │  │  ├─ admin/        # endpoints del panel del emprendedor
│  │  │  ├─ chatbot/       # endpoints/webhooks del chatbot WhatsApp
│  │  │  ├─ catalog/
│  │  │  ├─ faq/
│  │  │  ├─ calendar/
│  │  │  └─ auth/
│  ├─ core/                # configuración, seguridad, settings
│  ├─ db/                   # modelos SQLAlchemy, sesiones, migraciones (Alembic)
│  ├─ services/             # lógica de negocio (catálogo, turnos, contexto conversacional)
│  ├─ mcp/                  # cliente MCP, definición de tools/resources/prompts
│  ├─ schemas/              # modelos Pydantic (request/response)
│  └─ main.py               # entrypoint FastAPI
├─ tests/
├─ requirements.txt
└─ Dockerfile
└── README.md             # Este archivo
```

## ⚙️ Instalación y Ejecución

### 1. Clonar el repositorio e ingresar al directorio

```bash
cd backend
```

### 2. Crear entorno virtual

**Linux / Mac**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
SECRET_KEY=your_secret_key
```

### 5. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

---

> 💡 **Nota:** La aplicación estará disponible en `http://localhost:8000`.
