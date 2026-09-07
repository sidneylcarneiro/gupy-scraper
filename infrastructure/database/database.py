"""Configuracao da conexao com o PostgreSQL via SQLAlchemy (camada de infraestrutura).

Le a DATABASE_URL do arquivo .env (porta 5434 conforme configuracao do docker-compose).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://gupy:gupy@localhost:5434/gupy_scraper",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()