# Infraestructura — chatbot-comercial ☁️

Este directorio contiene las configuraciones de infraestructura, orquestación y despliegue del proyecto **chatbot-comercial**.

## 📁 Contenido

| Archivo / Directorio     | Descripción                                                   |
|--------------------------|---------------------------------------------------------------|
| `docker-compose.yml`     | Orquestación de servicios de soporte (PostgreSQL, Redis, Chroma) |
| `kubernetes/`            | Manifiestos de Kubernetes para despliegue en clúster           |
| `terraform/`             | Configuraciones de Terraform para infraestructura como código  |

## 🐳 Servicios con Docker Compose

El archivo `docker-compose.yml` levanta los servicios de soporte necesarios para el funcionamiento del proyecto:

| Servicio      | Descripción                                      |
|---------------|--------------------------------------------------|
| **PostgreSQL**| Base de datos relacional para persistencia histórica |
| **Redis**     | Cache en memoria y broker para Celery             |
| **Chroma**    | Base de datos vectorial para búsqueda semántica   |

### Uso

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar el estado de los servicios
docker-compose ps

# Detener los servicios
docker-compose down

# Eliminar volúmenes (datos persistentes)
docker-compose down -v
```

## ☸️ Kubernetes

Los manifiestos de Kubernetes se encuentran en el directorio `kubernetes/`. Permiten desplegar el proyecto en un clúster de Kubernetes.

### Comandos básicos

```bash
# Aplicar configuraciones
kubectl apply -f kubernetes/

# Verificar pods
kubectl get pods

# Ver logs de un pod
kubectl logs <pod-name>
```

## 🏗️ Terraform

Las configuraciones de Terraform en el directorio `terraform/` permiten gestionar la infraestructura cloud como código.

### Comandos básicos

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## 🔄 CI/CD

Los pipelines de CI/CD se configuran mediante **GitHub Actions** (ver `.github/workflows/` en la raíz del proyecto).

---

> 💡 **Nota:** Actualiza este README con configuraciones y ejemplos específicos del proyecto a medida que avance.
