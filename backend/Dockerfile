FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

# Instalación de dependencias del sistema de desarrollo, base de datos y herramientas de Git/SSH
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    openssh-client \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]