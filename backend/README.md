```markdown
# Chatbot Comercial Backend 🚀

Backend dockerizado para el Chatbot Comercial, desarrollado con FastAPI, PostgreSQL y Redis.

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
│   │   │   ├── admin/        # endpoints del panel del emprendedor
│   │   │   ├── chatbot/       # endpoints/webhooks del chatbot WhatsApp
│   │   │   ├── catalog/
│   │   │   ├── faq/
│   │   │   ├── calendar/
│   │   │   └── auth/
│   ├── core/                # configuración, seguridad, settings
│   ├── db/                   # modelos SQLAlchemy, sesiones, migraciones (Alembic)
│   ├── services/             # lógica de negocio (catálogo, turnos, contexto conversacional)
│   ├── mcp/                  # cliente MCP, definición de tools/resources/prompts
│   ├── schemas/              # modelos Pydantic (request/response)
│   └── main.py               # entrypoint FastAPI
├── tests/
├── requirements.txt
└── Dockerfile

```

## ⚙️ Configuración del Entorno (Onboarding)

Sigue estos pasos para levantar el entorno de desarrollo:

### 1. Clonar el repositorio

```bash
git clone <repo-url> && cd chatbot-comercial/backend

```

### 2. Crear .env local

Copia el archivo de ejemplo y ajusta las variables si es necesario (el default funciona con Docker).
**NUNCA** commitees el archivo `.env`.

```bash
cp .env.example .env

```

### 3. Levantar servicios con Docker

Este comando construye la imagen y levanta la API, PostgreSQL y Redis.

```bash
docker compose up --build

```

### 4. Verificar funcionamiento

* **Health Check**: [http://localhost:8000/health](https://www.google.com/search?q=http://localhost:8000/health)
* **Documentación Interactiva (Swagger)**: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)
* **Documentación Alternativa (Redoc)**: [http://localhost:8000/redoc](https://www.google.com/search?q=http://localhost:8000/redoc)

## 🔄 Live Reload

El código fuente local está mapeado al contenedor en `/backend`. Cualquier cambio que realices en los archivos `.py` locales reiniciará automáticamente el servidor Uvicorn dentro del contenedor.

## 🗄️ Migraciones de Base de Datos (Alembic)

Para generar y aplicar migraciones, utiliza los siguientes comandos (dentro del contenedor o vía `docker compose exec`):

```bash
# Generar una nueva migración
docker compose exec api alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
docker compose exec api alembic upgrade head

```

## 🛑 Detener Servicios

Para detener los contenedores:

```bash
docker compose down

```

Para borrar volúmenes (limpiar base de datos):

```bash
docker compose down -v

```

---

> 💡 **Nota importante**: No es necesario (ni está permitido según la política del proyecto) instalar Python, PostgreSQL o Redis directamente en tu máquina local. Todo se gestiona a través de Docker.

---

## Consideraciones de Entorno y Multiplataforma

Para garantizar que el entorno de desarrollo corra de forma optima y las herramientas de recarga en vivo funcionen correctamente, lee los siguientes requisitos segun tu configuracion.

### Metodo Recomendado: VS Code Dev Containers

El repositorio cuenta con soporte nativo para Dev Containers. Si utilizas VS Code, se recomienda abrir el proyecto dentro del contenedor. Esto automatiza la configuracion del interprete de Python, las extensiones del editor y el mapeo de herramientas como Git de forma aislada.

* Requiere la extension "Dev Containers" instalada en VS Code y Docker corriendo en segundo plano.
* Al abrir la carpeta del proyecto, presiona F1, selecciona "Dev Containers: Rebuild and Reopen in Container" y deja que el editor configure el entorno.

### Si usas Windows
1. Requisito obligatorio: Es indispensable tener instalado WSL 2 (Windows Subsystem for Linux) y Docker Desktop configurado para utilizar el backend de WSL 2. Sin esto, Docker no podra ejecutarse en tu sistema.
2. Si usas Dev Containers (Recomendado): Puedes abrir el proyecto directamente. Para obtener el maximo rendimiento de lectura/escritura y evitar demoras, se recomienda utilizar la opcion "Dev Containers: Clone Repository in Container Volume..." desde la paleta de comandos de VS Code.
3. Si NO usas Dev Containers: Al levantar el entorno mediante comandos tradicionales de Docker Compose en la terminal de Windows (CMD o PowerShell), NO clones este repositorio en el disco local de Windows (por ejemplo: C:/Users/...). Si lo haces, los volumenes compartidos impediran que el comando --reload de Uvicorn detecte los cambios en tus archivos.
4. Solucion sin Dev Containers: Abre tu terminal de WSL 2 (Ubuntu), muévete a tu directorio de usuario en Linux (cd ~), clona el proyecto dentro del sistema de archivos de Linux y ejecuta "docker compose up" desde alli. Esto garantiza que los volumenes compartidos funcionen correctamente y el entorno de desarrollo sea fluido.

### Si usas Mac (M1 / M2 / M3)

1. Asegurate de tener activada la opcion "Use Rosetta for x86/amd64 emulation on Apple Silicon" en la configuracion de Docker Desktop (General) para evitar fallos de compatibilidad con binarios especificos.
2. Las imagenes base del Dockerfile poseen soporte multiplataforma, por lo que el rendimiento en entornos ARM de Apple sera nativo y fluido.

### Si usas Linux Nativo o Dev Containers como Root

1. El contenedor de desarrollo corre internamente con el usuario root. Si ejecutas comandos dentro de la terminal del contenedor que generen archivos nuevos en el disco (tales como inicializaciones de Alembic, creacion de modelos o entornos virtuales), estos archivos se guardaran en tu sistema operativo host con permisos de administrador bloqueados.
2. Si experimentas problemas para editar o eliminar archivos creados por el contenedor desde tu entorno local, puedes recuperar la propiedad de los mismos ejecutando en tu terminal local:
sudo chown -R $USER:$USER .

```

```