# Deploy — Chatbot Comercial

> Pasos para desplegar la aplicación en un entorno nuevo o reconstruir desde cero.

## Requisitos previos

- Docker y Docker Compose instalados
- Python 3.11+ con `pip`
- Acceso a los números de WhatsApp Business configurados en Meta

## 1. Clonar y preparar entorno

```bash
git clone https://github.com/dgimenezdeveloper/chatbot-comercial.git
cd chatbot-comercial
git checkout features/data-models
```

## 2. Levantar infraestructura

```bash
cd repositorio
docker compose up -d postgres redis
```

Esto levanta PostgreSQL 16 y Redis 7. Esperar ~10 segundos a que estén listos.

## 3. Crear tablas (migración Alembic)

```bash
cd repositorio/backend
pip install -r requirements.txt
alembic upgrade head
```

## 4. Insertar datos de prueba (seed)

```bash
python -m app.data_seed
```

Verificar que la salida no muestra errores. El seed crea:
- 1 negocio de prueba (business_id=1)
- Usuarios, servicios, productos de ejemplo
- ~8 sesiones de conversación con ~50 eventos
- 5 calificaciones CSAT de prueba

## 5. Levantar aplicación completa

```bash
cd repositorio
docker compose up -d
```

Servicios que se levantan:
| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `backend` | 8000 | API FastAPI |
| `frontend` | 3000 | Panel Next.js |
| `postgres` | 5432 | Base de datos |
| `redis` | 6379 | Broker Celery + caché |
| `celery-worker` | — | Scheduler de recordatorios |

## 6. Verificar despliegue

```bash
# Health check del backend
curl http://localhost:8000/api/v1/admin/health

# Métricas base (deberían retornar datos reales, no ceros)
curl "http://localhost:8000/api/v1/admin/metrics?days=30&business_id=1"
```

## 7. Migraciones futuras

Cuando se agreguen nuevas tablas o columnas:

```bash
cd repositorio/backend
alembic revision --autogenerate -m "descripcion_del_cambio"
# Revisar el archivo generado en alembic/versions/
alembic upgrade head
python -m app.data_seed  # si hay nuevo seed data
```

## Rollback

```bash
# Volver una migración atrás
cd repositorio/backend
alembic downgrade -1

# Limpiar todo
cd repositorio
docker compose down -v  # ¡Elimina volúmenes y datos!
```
