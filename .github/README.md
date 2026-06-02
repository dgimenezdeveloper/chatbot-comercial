# .github

Configuración de GitHub para el repositorio `chatbot-comercial`.

---

## Contenido

### CODEOWNERS

Define los responsables de revisión por área del proyecto. GitHub asigna automáticamente
estos usuarios como reviewers cuando se abre un PR que modifica archivos en su área.

| Ruta | Responsables |
|------|-------------|
| `/backend/` | dgimenezdeveloper, rcrossa, dario923, arielrz-dev |
| `/frontend/` | manfredcamacho, rcrossa, Arleni1108, Aleska19 |
| `/data/` | rcrossa, vmvillamar |
| `/qa/` | rcrossa, yaninaemail2024-hub, ariasari7066-oss, matlobos |
| `/ux-ui/` | DanaStornello, Viky-dotcom |
| `/infra/` | rcrossa, dgimenezdeveloper, dario923, arielrz-dev |
| `/.github/` | rcrossa, dgimenezdeveloper |

### workflows/

Contiene los workflows de GitHub Actions del proyecto.

| Archivo | Descripcion |
|---------|-------------|
| `auto-move-issues.yml` | Mueve automaticamente las tarjetas del Project Board segun el estado de issues y PRs |
| `strict-roles.yml` | Valida que los PRs sean abiertos unicamente hacia las branches permitidas segun el area del contribuidor |

Ver [workflows/README.md](workflows/README.md) para la documentacion completa de `auto-move-issues.yml`.

---

## Permisos y acceso

Los merges a la branch `develop` estan restringidos a:

- `dgimenezdeveloper`
- `rcrossa`

El resto del equipo contribuye mediante Pull Requests que requieren al menos una aprobacion
antes de poder ser mergeados.

---

## Configuracion requerida

Para que los workflows funcionen correctamente, el repositorio debe tener configurados:

**Secrets** (Settings → Secrets and variables → Actions → Secrets):

| Nombre | Descripcion |
|--------|-------------|
| `PROJECT_TOKEN` | PAT clasico con scopes: `project`, `repo`, `read:org` |

**Variables** (Settings → Secrets and variables → Actions → Variables):

| Nombre | Descripcion | Ejemplo |
|--------|-------------|---------|
| `PROJECT_NUMBER` | Numero del proyecto en GitHub Projects | `5` |
| `ORGANIZATION` | Username del owner del proyecto | `dgimenezdeveloper` |
| `QA_GITHUB_USERS` | Usernames de los testers QA separados por espacio | `tester1 tester2` |
