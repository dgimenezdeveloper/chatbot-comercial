from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import settings

# Evita tener que escribir manualmente '?sslmode=require' en entornos de producción
db_url = settings.DATABASE_URL

# Si detecta que la base de datos es de Azure y no tiene el parámetro sslmode, lo añade automáticamente
if "postgres.database.azure.com" in db_url and "sslmode" not in db_url:
    if "?" in db_url:
        db_url += "&sslmode=require"
    else:
        db_url += "?sslmode=require"

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Importar todos los modelos para que Base.metadata los registre
import app.db.models  # noqa: E402, F401

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()