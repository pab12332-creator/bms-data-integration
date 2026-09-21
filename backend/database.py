from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cadena de conexión a tu PostgreSQL local (ajusta tu usuario y contraseña si es necesario)
DATABASE_URL = "postgresql://postgres:Admin12345@localhost:5432/BMS_OXXO"
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Se habilita echo=True temporalmente para auditoría de SQL
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de base de datos en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()