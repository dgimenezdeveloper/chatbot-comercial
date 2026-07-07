# Data — chatbot-comercial 📊

Este directorio contiene los datos, scripts de procesamiento y documentación relacionados con el análisis de datos del proyecto **chatbot-comercial**.

## 📁 Contenido

| Directorio       | Descripción                                                          |
|------------------|----------------------------------------------------------------------|
| `/raw`           | Datos crudos obtenidos de fuentes externas (CSV, JSON, logs, etc.)   |
| `/processed`     | Datos limpios y transformados listos para análisis                   |
| `/scripts`       | Scripts de ETL, limpieza y transformación (Python / SQL)             |
| `/queries`       | Consultas SQL para extracción y análisis                             |
| `/reports`       | Reportes generados (PDF, notebooks, dashboards)                      |
| `/schemas`       | Definiciones de esquemas y diccionarios de datos                     |

## 🛠️ Stack Sugerido

- **Lenguaje:** Python
- **Librerías:** Pandas, NumPy, SQLAlchemy
- **Visualización:** Matplotlib, Seaborn, Plotly
- **Base de datos:** PostgreSQL / BigQuery (según definición del equipo)
- **Orquestación:** Airflow / Prefect (opcional)

## ⚙️ Uso Rápido

1. **Coloca los datos crudos** en `raw/`.
2. **Ejecuta los scripts de limpieza** en `scripts/`:

   ```bash
   python scripts/clean_data.py
   ```

3. **Los datos procesados** se guardarán en `processed/`.
4. **Ejecuta consultas de análisis** desde `queries/` o los notebooks en `reports/`.

## 📋 Convenciones

- No subir datos sensibles o con PII al repositorio.
- Documentar cada transformación en el script correspondiente.
- Mantener actualizado el diccionario de datos en `schemas/`.
- Usar nomenclatura clara y consistente en los archivos (snake_case).

---

> 💡 **Nota:** Actualiza este README con enlaces y ejemplos específicos del proyecto a medida que avance.
