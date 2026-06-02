# Frontend — chatbot-comercial 🎨

Este directorio contiene el código fuente y la configuración del frontend del proyecto **chatbot-comercial**, una aplicación web para la gestión e interacción con chatbots comerciales. Está integrado como un subproyecto dentro de la arquitectura de **Monorepo** del equipo.

## 🛠️ Tecnologías Core

| Tecnología           | Selección Oficial                                    | Descripción / Justificación |
|----------------------|-----------------------------------------------------|-----------------------------|
| **Framework** | React 19 + Vite (SPA)                               | Solución ligera, ágil y de alta performance; evita la sobrecarga de servidor de Next.js. |
| **Lenguaje** | TypeScript                                          | Tipado estricto para asegurar la robustez del código y consistencia de datos. |
| **Estilos** | Tailwind CSS + Shadcn/UI                            | Utilidades de diseño atómico alineadas con el sistema de diseño de UX/UI en Figma. |
| **Estado** | Zustand                                             | Gestor de estado global ultraligero, ideal para el historial de mensajes del chat. |
| **HTTP / WS** | Axios + WebSockets nativos                          | Conexión con FastAPI y consumo de eventos en tiempo real para el streaming de respuestas. |
| **Testing** | Vitest + Cypress                                    | Pruebas unitarias veloces e integración end-to-end automatizada desde el inicio. |
| **Storybook** | Storybook                                           | Entorno de desarrollo aislado para validación directa de componentes con UX/UI. |

## 📁 Estructura del Proyecto

```bash
frontend/
├── .storybook/              # Configuración de Storybook
├── public/                  # Archivos estáticos (favicon, imágenes del catálogo, etc.)
├── src/
│   ├── components/          # Componentes reutilizables e interactivos
│   │   ├── ui/              # Componentes de base atómica (Shadcn/UI)
│   │   ├── chatbot/         # Ventana de conversación, burbujas y formularios interactivos
│   │   └── dashboard/       # Paneles para visualización de métricas y leads comerciales
│   ├── hooks/               # Custom hooks (ej: useWebSocket, useAuth)
│   ├── services/            # Clientes de API, abstracción de endpoints y mocks de datos
│   ├── store/               # Stores de Zustand (historial de chat, UI state)
│   ├── types/               # Tipos e interfaces globales de TypeScript
│   ├── utils/               # Funciones utilitarias y formateadores
│   ├── App.tsx              # Componente raíz
│   └── main.tsx             # Punto de entrada de Vite
├── .env.example             # Variables de entorno de ejemplo
├── .prettierrc              # Configuración estricta de formateo
├── eslint.config.js         # Configuración de ESLint con TypeScript y React hooks
├── tsconfig.json            # Configuración de TypeScript
└── README.md                # Este archivo
```

## ✅ Requisitos Previos

- **Node.js** >= 18.x
- **pnpm** >= 9.x (Gestor de paquetes exclusivo del Monorepo).
- ⚠️ **PROHIBIDO EL USO DE NPM / YARN:** Por políticas de consistencia en los workspaces del monorepo, el uso de npm o yarn está prohibido. Toda dependencia externa debe instalarse mediante `pnpm`.

## ⚙️ Configuración e Instalación

1. **Instala las dependencias desde este directorio:**

   ```bash
   pnpm install
   ```

2. **Copia el archivo de variables de entorno y completa los valores correspondientes:**

   ```bash
   cp .env.example .env.local
   ```

## 🚀 Scripts Disponibles

| Script             | Comando | Descripción |
|--------------------|---------|-------------|
| **Desarrollo** | `pnpm dev` | Inicia el servidor de desarrollo local con Vite (`http://localhost:5173`). |
| **Build** | `pnpm build` | Compila y genera el bundle optimizado para producción de la SPA. |
| **Linter** | `pnpm lint` | Ejecuta el análisis estático de código con ESLint. |
| **Format** | `pnpm format` | Formatea automáticamente el código utilizando Prettier. |
| **Storybook** | `pnpm storybook` | Inicia el entorno aislado de componentes en `http://localhost:6006`. |
| **Testing** | `pnpm test` | Ejecuta las pruebas unitarias y de integración con Vitest. |
| **Testing E2E** | `pnpm test:e2e` | Abre la interfaz de Cypress para pruebas de extremo a extremo. |

## 🔐 Variables de Entorno

| Variable              | Descripción                                     | Ejemplo                          |
|-----------------------|-------------------------------------------------|----------------------------------|
| `VITE_API_BASE_URL`   | URL base de la API REST del backend (FastAPI)   | `http://localhost:8000/api/v1`   |
| `VITE_WS_CHAT_URL`    | URL del WebSocket para el flujo del chatbot     | `ws://localhost:8000/chat/ws`    |

## 📋 Convenciones del Proyecto

- **Nomenclatura:** `kebab-case` para nombres de carpetas, archivos de configuración, hooks y utilidades (ej: `use-websocket.ts`). `PascalCase` estrictamente para componentes React y archivos de Storybook (ej: `ChatWindow.tsx`).
- **Control de Calidad Local:** El proyecto utiliza **Husky** y **lint-staged**. Cualquier commit que contenga errores de sintaxis, tipos o formato será rechazado de manera automática antes de confirmarse en Git.
- **Mensajes de Commit:** Es mandatorio seguir la especificación de [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, `docs:`).

## 🔗 Recursos del Equipo

- Documentación de la API (FastAPI - Swagger): _(añadir URL)_
- Diseños en Figma: [Link](https://www.figma.com/design/MRIDdLhLsGWQbBRt8my5Tm/Dise%C3%B1o-UXUI-Equipo-10-InnovaLab?node-id=27-76&t=PZWYmXb0sUN7mr2N-0) 
- Tablero de Gestión: [Link](https://github.com/users/dgimenezdeveloper/projects/6)