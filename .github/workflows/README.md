# Workflow: Auto Move Issues — Project Board

Documentación del workflow `.github/workflows/auto-move-issues.yml` que automatiza
el movimiento de tarjetas en el **GitHub Projects v2** a lo largo del ciclo de vida de issues y PRs.

---

## Flujo de estados

```
BACKLOG
    |
    | issue asignada a un dev
    v
READY
    |
    | dev crea branch (ej: feature/42-login)
    v
IN PROGRESS
    |
    | dev abre PR con "closes #N" en el body
    v
IN REVIEW  <----------------------------------------------+
    |                                                      |
    | QA hace Review: Request Changes                      |
    +------------------------------------------------------+
    |
    | QA hace Review: Approve
    v
QA APPROVED
    |
    | dgimenezdeveloper o rcrossa mergean el PR a develop
    v
DONE
```

**Caso especial:** Si un PR se cierra **sin mergear**, las issues vinculadas vuelven a **Backlog**.

---

## Columnas requeridas en el Project Board

Crear el campo **"Status"** (Single Select) con exactamente estas opciones:

| Columna | Descripción |
|---------|-------------|
| `Backlog` | Issues sin asignar o drafts |
| `Ready` | Issue asignada, dev preparado para iniciar |
| `In Progress` | Desarrollo en curso (branch activa) |
| `In Review` | PR abierto, pendiente aprobación QA |
| `QA Approved` | QA aprobó, listo para mergear por maintainers |
| `Done` | Mergeado a `develop` exitosamente |

>  Los nombres deben coincidir **exactamente** (mayúsculas y espacios) con los valores de arriba.

---

## Integración QA (Jira + GitHub)

Los testers QA usan Jira como herramienta principal, pero deben aprobar PRs en GitHub.

### Cómo funciona

1. **QA recibe notificación por email** cuando un PR es abierto (el workflow comenta mencionando a los QA)
2. **QA puede hacer la review directamente desde el email** o entrando a GitHub
3. El workflow detecta si el reviewer es QA via la variable `QA_GITHUB_USERS`
4. **Si QA Aprueba** → la card pasa a "QA Approved" y los maintainers reciben un comentario con `@dgimenezdeveloper @rcrossa`
5. **Si QA Rechaza** → la card vuelve a "In Progress" y el dev recibe un comentario con el link a los comentarios del QA

### Requisitos para los QA

- Los testers QA deben tener una cuenta de GitHub (aunque sea básica)
- Sus usernames de GitHub deben estar en la variable `QA_GITHUB_USERS`
- GitHub les enviará notificaciones por email automáticamente cuando sean mencionados

### No tienen cuenta de GitHub

Si los QA no tienen cuenta de GitHub, pueden solicitar a un maintainer que agregue manualmente
el label `qa-approved` al PR. El workflow también puede extenderse para detectar eventos de labels.

---

## Convención de nombres de branches

Para que el workflow detecte automáticamente la issue al crear una branch, usá cualquiera de estos formatos:

| Formato | Ejemplo | Issue detectada |
|---------|---------|-----------------|
| `{número}-{título}` | `42-login-usuario` | #42 |
| `feature/{número}-{título}` | `feature/42-login` | #42 |
| `fix/{número}-{título}` | `fix/42-bug-login` | #42 |
| `hotfix/{número}-{título}` | `hotfix/42` | #42 |

**Tip:** Usar el botón **"Create a branch"** en la propia issue de GitHub genera la branch
con el nombre correcto automáticamente.

---

## Vincular PRs a issues

Para que el workflow mueva las issues cuando el PR cambia de estado, el body del PR
debe incluir una de estas palabras clave seguida del número de issue:

```
closes #42
fixes #42
resolves #42
close #42
fix #42
resolve #42
```

**Ejemplo de body de PR:**
```markdown
## Descripción
Implementa el login de usuario con JWT.

Closes #42
Closes #43
```

---

## Labels automáticos

El workflow gestiona automáticamente estos labels en los PRs:

| Label | Color | Cuándo se agrega |
|-------|-------|------------------|
| `needs-qa` | Amarillo | PR abierto o reabierto |
| `qa-approved` | Verde | QA aprueba el PR |
| `qa-rejected` | Rojo | QA rechaza el PR |
| `ready-to-merge` | Azul | Junto con qa-approved |
| `merged` | Morado | PR mergeado a develop |

---

## Jobs del workflow

| Job | Trigger | Acción |
|-----|---------|--------|
| `move_to_ready` | `issues.assigned` | Issue → Ready |
| `move_to_backlog_unassigned` | `issues.unassigned` | Issue → Backlog |
| `move_to_in_progress` | `create` (branch) | Issue extraída de la branch → In Progress |
| `move_to_in_review` | `pull_request.opened/reopened` | Issues vinculadas → In Review + notifica QA |
| `handle_qa_review` | `pull_request_review.submitted` | QA Aprueba → QA Approved + notifica maintainers; QA Rechaza → In Progress + notifica dev |
| `move_to_done` | `pull_request.closed` (merged=true) | Issues vinculadas → Done |
| `move_to_backlog_closed_pr` | `pull_request.closed` (merged=false) | Issues vinculadas → Backlog |

---

## Troubleshooting

### El workflow no mueve la tarjeta

1. Verificar que el secret `PROJECT_TOKEN` existe y tiene los scopes correctos (`project`, `repo`, `read:org`)
2. Verificar que las variables `PROJECT_NUMBER`, `ORGANIZATION`, `QA_GITHUB_USERS` están configuradas
3. Verificar que los nombres de columna en el Project Board coinciden exactamente con los del workflow
4. Revisar los logs del workflow en **Actions** del repositorio

### El workflow falla con "Resource not accessible by integration"

El `PROJECT_TOKEN` no tiene los permisos correctos. Regenerar el PAT con los scopes `project`, `repo`, `read:org`.

### La issue no se detecta al crear la branch

El nombre de la branch no contiene un número de issue. Seguir la convención de nombres descripta arriba.

### QA no recibe notificaciones

Verificar que el username de GitHub del QA está en la variable `QA_GITHUB_USERS` (separado por espacio de otros usernames).
