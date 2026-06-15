# Frontend — chatbot-comercial 🎨

Este directorio contiene el código fuente y la configuración del frontend del proyecto **chatbot-comercial**. La aplicación funciona como una **Landing Page** y un **Panel de Administración (SaaS)** para comercios (actualmente enfocado en la gestión de Peluquerías). 

> **Nota para Desarrolladores:** El proyecto está diseñado con un enfoque "Backend-heavy". Las integraciones complejas (flujos de WhatsApp, motores de inferencia, Google Calendar) ocurren en el servidor. El Frontend se encarga puramente de la presentación comercial, el onboarding del comercio y la gestión visual de los turnos.

## 🛠️ Stack Tecnológico

| Tecnología | Caso de Uso |
| :--- | :--- |
| **Next.js (App Router)** | Framework principal (React). Manejo de rutas, Landing Page optimizada y Dashboard. |
| **JavaScript (ES6+)** | Lenguaje principal (Archivos `.js` / `.jsx`). |
| **Tailwind CSS + Shadcn/UI** | Sistema de diseño, estilos utilitarios y componentes accesibles base. |
| **NextAuth.js (Auth.js)** | Gestión de sesiones y autenticación (Google Provider & Credentials Mock). |
| **React Context API** | Estado global nativo para datos ligeros en el cliente. |
| **TanStack Query** | Data fetching, caché y sincronización asíncrona con el servidor. |
| **Axios** | Cliente HTTP configurado para las peticiones REST al Backend (FastAPI). |

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu máquina:
- **Node.js** (v18.17.0 o superior recomendada).
- **pnpm** (v9.x). 

⚠️ **CRÍTICO:** El uso de `npm` o `yarn` está terminantemente prohibido para mantener la integridad de los workspaces en el Monorepo.

## ⚙️ Configuración Local

Sigue estos pasos para levantar el entorno de desarrollo local sin afectar la base de datos de producción.

1. **Instalar dependencias:**
   Posicionado en la raíz de la carpeta `/frontend`, ejecuta:
   ```bash
   pnpm install
   ```

2. **Configurar variables de entorno:**
   Crea tu archivo de entorno local copiando la plantilla.
   ```bash
   cp .env.example .env.local
   ```
   *Nota: Solicita al administrador del repositorio los valores reales de los IDs de Google Auth y el Secret de NextAuth.*

3. **Iniciar el servidor de desarrollo:**
   ```bash
   pnpm dev
   ```
   La aplicación estará disponible en `http://localhost:3000`.

## 📁 Estructura del Proyecto

La arquitectura sigue el patrón del App Router de Next.js, agrupando las vistas por contexto lógico y separando la UI de la lógica de peticiones:

```text
frontend/
├── public/                  # Archivos estáticos (favicon, imágenes, logos)
├── src/
│   ├── app/                 # Enrutador principal (Next.js App Router)
│   │   ├── (marketing)/     # Grupo de rutas: Landing page y pre-venta (Públicas)
│   │   ├── (auth)/          # Grupo de rutas: Login y Registro (Públicas)
│   │   └── (dashboard)/     # Grupo de rutas: Onboarding y Panel de control (Privadas)
│   ├── components/
│   │   ├── ui/              # Componentes primitivos (Shadcn/UI base)
│   │   ├── layout/          # Estructuras globales (Sidebar, Navbar, Footers)
│   │   └── features/        # Componentes complejos (ej. AppointmentsTable, SetupForm)
│   ├── hooks/               # Custom React hooks (ej. useAppointments)
│   ├── lib/                 # Configuración de librerías (Axios instance, Tailwind utils)
│   └── services/            # Funciones de fetching que interactúan con la API
├── .env.example             # Plantilla segura de variables de entorno
├── jsconfig.json            # Configuración de path aliases (@/*)
└── package.json             # Manejo de dependencias y scripts
```

## 🗺️ Mapa de Rutas (Navegación)

La aplicación utiliza el sistema de enrutamiento basado en el sistema de archivos de Next.js (App Router). A continuación se detallan las rutas principales accesibles para el usuario:

| Ruta | Vista / Componente | Grupo de Ruta | Nivel de Acceso |
| :--- | :--- | :--- | :--- |
| `/` | Landing Page | `(marketing)` | Público |
| `/login` | Login Page | `(auth)` | Público |
| `/register` | Register Page | `(auth)` | Público |
| `/onboarding` | Onboarding Page | `(dashboard)` | Privado (Requiere Auth) |
| `/dashboard` | Dashboard Page | `(dashboard)` | Privado (Requiere Auth) |

## 🔐 Variables de Entorno (`.env.example`)

Asegúrate de que tu archivo `.env.local` contenga la siguiente estructura. Las claves reales no deben subirse a Git.

### Explicación de Variables:
* **`NEXT_PUBLIC_API_URL`**: Necesaria para que Axios sepa a qué puerto pegarle al backend (FastAPI). Lleva el prefijo `NEXT_PUBLIC_` para que Next.js permita que el código del lado del cliente (navegador) acceda a esta variable.
* **`NEXTAUTH_URL`**: NextAuth la utiliza internamente para resolver las redirecciones y callbacks de forma segura.
* **`NEXTAUTH_SECRET`**: Una cadena aleatoria que NextAuth exige para encriptar los JWT (JSON Web Tokens) de las sesiones de usuario.
* **`GOOGLE_CLIENT_...`**: Credenciales otorgadas por Google Cloud Console para habilitar el login con Gmail en nuestra plataforma.

```env
# API Config (Expuesta al cliente)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# NextAuth Config (Solo servidor)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_super_secret_key_here

# Google OAuth Credentials (Solo servidor)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

## 📜 Scripts

| Script | Comando | Descripción |
| :--- | :--- | :--- |
| `dev` | `pnpm dev` | Inicia el servidor de desarrollo con Hot Module Replacement (HMR). |
| `build` | `pnpm build` | Compila la aplicación para el entorno de producción. |
| `start` | `pnpm start` | Inicia el servidor de producción usando los archivos compilados en el build. |
| `lint` | `pnpm lint` | Ejecuta ESLint para analizar estáticamente el código y buscar errores. |
| `format` | `pnpm format` | Formatea el código automáticamente usando Prettier. |

## 🤝 Convenciones de Desarrollo

Para mantener el código limpio y facilitar el trabajo cruzado entre los miembros del equipo, cumplimos estas reglas estandarizadas:

1. **Idioma Oficial del Código:** Todo el código fuente (nombres de variables, funciones, componentes, nombres de archivos y comentarios técnicos) debe escribirse estrictamente en **inglés** para mantener un estándar profesional en la industria. La documentación (como este README) y los textos visibles para el usuario final van en español. *(Ejemplo: crear el archivo `use-appointments.js` en lugar de `use-turnos.js`)*.
2. **Componentes "Client" vs "Server":** Por defecto, el App Router de Next.js renderiza componentes en el servidor (Server Components). Si el archivo que estás creando requiere hooks de React (`useState`, `useEffect`) o maneja interactividad del usuario (`onClick`, `onChange`), **debes agregar obligatoriamente la directiva `"use client";`** en la primera línea del archivo.
3. **Nomenclatura de Archivos:** * `PascalCase.jsx` para Componentes visuales de React (ej. `DashboardSidebar.jsx`).
   * `kebab-case.js` para hooks, utilidades y servicios de API (ej. `use-appointments.js`, `api-client.js`).
4. **Estilos:** Se utilizarán exclusivamente las clases utilitarias de Tailwind CSS. Evitar la creación de archivos `.css` separados a menos que sea estrictamente necesario para variables globales.
5. **Calidad de Git (Pre-commit hooks):** El repositorio local tiene configurado Husky. El sistema bloqueará cualquier intento de `git commit` si los archivos modificados no pasan las reglas de ESLint o no cumplen con el formato de [Conventional Commits](https://www.conventionalcommits.org/).