from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Importar todos los modelos para que Base.metadata los registre
# (necesario para create_all() y Alembic autogenerate)
import app.db.models  # noqa: E402, F401

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
