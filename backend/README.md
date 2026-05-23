# Backend — Python API 🐍

Backend desarrollado en Python siguiendo una arquitectura simple y escalable.

## 🚀 Tecnologías

- **Python** 3.11+
- **FastAPI** / Flask (según implementación)
- **PostgreSQL** / MySQL
- **SQLAlchemy**
- **Docker**
- **JWT Authentication**

## 📁 Estructura del Proyecto

```bash
backend/
│
├── app/
│   ├── controllers/      # Controladores de la lógica de negocio
│   ├── services/         # Servicios de aplicación
│   ├── repositories/     # Capa de acceso a datos
│   ├── models/           # Modelos de datos / ORM
│   ├── routes/           # Definición de rutas/endpoints
│   ├── middlewares/      # Middlewares (autenticación, logging, etc.)
│   ├── config/           # Configuración de la aplicación
│   └── main.py           # Punto de entrada de la aplicación
│
├── requirements.txt      # Dependencias del proyecto
├── .env                  # Variables de entorno
├── Dockerfile            # Configuración Docker
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
