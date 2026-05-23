# Chatbot Comercial Avanzado 🤖

## Descripción del Proyecto

Este proyecto está diseñado para revolucionar la interacción comercial mediante el uso de IA avanzada y la implementación de agentes autónomos, eliminando las limitaciones de los antiguos sistemas de flujo estricto.

## Stack Tecnológico

La arquitectura está diseñada para procesar IA de forma nativa, mantener contexto conversacional eficiente y escalar la infraestructura.

| Componente               | Tecnologías Seleccionadas                          |
|--------------------------|----------------------------------------------------|
| Backend / API Gateway    | Python, FastAPI, Pydantic                          |
| Procesamiento Asíncrono  | Celery + Redis                                     |
| Gestión de IA / Contexto | Model Context Protocol (MCP), Redis (Hot Cache)    |
| Frontend                 | React, TypeScript, Vite, Tailwind CSS, shadcn/ui   |
| Bases de Datos           | PostgreSQL (Persistencia histórica), Chroma / Milvus (Vector DB) |
| Canal de Mensajería      | WhatsApp Cloud API (Oficial de Meta)               |
| QA / Pruebas             | Cypress (E2E), Pytest (Backend)                    |
| Infraestructura / CI&CD  | Docker, Kubernetes, Terraform, GitHub Actions      |

## 📂 Estructura del Monorepo

El código está organizado por dominios para que cada equipo pueda trabajar con autonomía mientras se mantiene la integración continua.

> **Nota:** Ingresá al README de cada directorio para ver las instrucciones específicas de levantamiento, scripts y convenciones de cada área.

| Directorio                                           | Descripción                                                                 |
|------------------------------------------------------|-----------------------------------------------------------------------------|
| 🔗[backend](/backend/README.md)                     | API orquestadora en FastAPI, gestión de contexto conversacional en 3 capas, servidores MCP e integración webhooks de WhatsApp |
| 🔗[frontend](/frontend/README.md)                   | React + Vite, Storybook para componentes aislados y WebSockets para streaming de IA |
| 🔗 [data](/data/README.md)                           | Scripts ETL, notebooks, diseño del esquema relacional (PostgreSQL) y analítica |
| 🔗 [ux-ui](/ux-ui/README.md)                         | Documentación de flujos conversacionales, límites de IA, feedback visual y diseño de interfaz base |
| 🔗 [qa](/qa/README.md)                               | Planes de prueba, automatización con Cypress, smoke tests y estrategias de validación de alucinaciones del LLM |
| 🔗 [infra](/infra/README.md)                         | Archivos docker-compose.yml, manifiestos de Kubernetes y configuraciones de despliegue |
| 🔗 [github](.github/README.md)   | Workflows de GitHub Actions, templates para Issues y Pull Requests |

## 🚀 Cómo Empezar

1. **Cloná este repositorio**

   ```bash
   git clone https://github.com/Jann-CH/chatbot-comercial.git
   cd chatbot-comercial
   ```

2. **Levantá los servicios de soporte segun tu rol**

   Revisá el archivo `docker-compose.yml` en la carpeta `infra/` para levantar los servicios de soporte (PostgreSQL, Redis, Chroma).

3. **Ingresá a la carpeta de tu disciplina**

   ```bash
   cd backend   # o frontend, data, ux-ui, qa, infra
   ```

   Y seguí las instrucciones de su respectivo `README.md`.
