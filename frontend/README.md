# Frontend — chatbot-comercial 🎨

Este directorio contiene el código fuente y la configuración del frontend del proyecto **chatbot-comercial**, una aplicación web para la gestión e interacción con chatbots comerciales.

## 🛠️ Tecnologías Principales

| Tecnología           | Descripción                                         |
|----------------------|-----------------------------------------------------|
| **Framework**        | React / Next.js (según definición del equipo)       |
| **Lenguaje**         | TypeScript                                          |
| **Estilos**          | CSS Modules / Tailwind CSS / Styled Components      |
| **Estado**           | React Context / Zustand (según definición del equipo) |
| **HTTP Client**      | Axios / Fetch API                                   |
| **Testing**          | Jest + React Testing Library / Vitest               |
| **Storybook**        | Desarrollo y documentación de componentes aislados  |

## 📁 Estructura del Proyecto

```bash
frontend/
├── public/                  # Archivos estáticos (favicon, imágenes, etc.)
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── common/          # Componentes genéricos (botones, inputs, modales)
│   │   └── chatbot/         # Componentes específicos del chatbot
│   ├── pages/               # Páginas/rutas de la aplicación
│   ├── hooks/               # Custom hooks
│   ├── services/            # Llamadas a APIs y lógica de negocio
│   ├── store/               # Estado global (si aplica)
│   ├── types/               # Definiciones de tipos TypeScript
│   ├── utils/               # Funciones utilitarias
│   └── styles/              # Estilos globales y temas
├── stories/                 # Stories de Storybook
├── tests/                   # Pruebas unitarias y de integración
├── .env.example             # Variables de entorno de ejemplo
├── tsconfig.json            # Configuración de TypeScript
├── package.json             # Dependencias y scripts
├── .storybook/              # Configuración de Storybook
└── README.md                # Este archivo
```

## ✅ Requisitos Previos

- **Node.js** >= 18.x
- **NO USAR NPM** — Evitemos vulnerabilidades o riesgos de seguridad. Usar **yarn** o **pnpm**.

## ⚙️ Instalación

1. **Instala las dependencias:**

   ```bash
   yarn install
   # o
   pnpm install
   ```

2. **Copia el archivo de variables de entorno y completa los valores:**

   ```bash
   cp .env.example .env.local
   ```

## 🚀 Uso

### Desarrollo

Inicia el servidor de desarrollo:

```bash
yarn dev
# o
pnpm dev
```

La aplicación estará disponible en `http://localhost:3000`.

### Producción

Construye la aplicación para producción:

```bash
yarn build
# o
pnpm build
```

Inicia el servidor de producción:

```bash
yarn start
# o
pnpm start
```

### Storybook

Explora componentes ejecutando Storybook:

```bash
yarn storybook
# o
pnpm storybook
```

Storybook estará disponible en `http://localhost:6006`.

Para generar la build estática de Storybook:

```bash
yarn build-storybook
# o
pnpm build-storybook
```

### Pruebas

Ejecuta las pruebas:

```bash
yarn test
# o
pnpm test
```

## 🔐 Variables de Entorno

| Variable               | Descripción                          | Ejemplo                          |
|------------------------|--------------------------------------|----------------------------------|
| `NEXT_PUBLIC_API_URL`  | URL base de la API del backend       | `http://localhost:4000/api`      |
| `NEXT_PUBLIC_WS_URL`   | URL del WebSocket (si aplica)        | `ws://localhost:4000`            |
| `NEXT_PUBLIC_APP_NAME` | Nombre de la aplicación              | `Chatbot Comercial`              |

## 📜 Scripts Disponibles

| Script             | Descripción                                    |
|--------------------|------------------------------------------------|
| `dev`              | Inicia el servidor de desarrollo               |
| `build`            | Construye la aplicación para producción        |
| `start`            | Inicia el servidor de producción               |
| `storybook`        | Inicia Storybook para desarrollo de componentes|
| `build-storybook`  | Genera la build estática de Storybook          |
| `test`             | Ejecuta las pruebas                            |
| `lint`             | Ejecuta el linter                              |
| `format`           | Formatea el código con Prettier                |

## 📋 Convenciones de Código

- **Nomenclatura:** `camelCase` para variables y funciones, `PascalCase` para componentes y tipos.
- **Componentes:** un componente por archivo, exportación nombrada por defecto.
- **Estilos:** seguir la metodología definida en el equipo (CSS Modules, Tailwind, etc.).
- **Commits:** seguir [Conventional Commits](https://www.conventionalcommits.org/).

## 🤝 Contribuir

1. Crea una rama con el prefijo `feature/`, `fix/` o `chore/`.
2. Realiza los cambios y asegúrate de que las pruebas pasen.
3. Abre un Pull Request describiendo los cambios realizados.

## 🔗 Recursos y Enlaces

- Documentación de la API: _(añadir URL)_
- Diseños en Figma: _(añadir URL)_
- Tablero del proyecto: _(añadir URL)_

## 📄 Licencia

Indicar la licencia del proyecto o heredada del repo principal.

---

> 💡 **Nota:** Actualiza este README con enlaces y ejemplos específicos del proyecto a medida que avance.
