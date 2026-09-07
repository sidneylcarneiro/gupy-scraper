"""Modelos ORM (SQLAlchemy) da camada de infraestrutura."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.vaga import FormatoTrabalho, StatusVaga
from infrastructure.database.database import Base


class VagaModel(Base):
    """Mapeamento da entidade de dominio Vaga para a tabela 'vagas'."""

    __tablename__ = "vagas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    localizacao: Mapped[str] = mapped_column(String(255), nullable=False)
    formato: Mapped[str] = mapped_column(
        Enum(FormatoTrabalho, name="formato_trabalho_enum", native_enum=False), nullable=False
    )
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    data_publicacao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(StatusVaga, name="status_vaga_enum", native_enum=False), nullable=False, default=StatusVaga.ATIVA.value
    )


class BuscaModel(Base):
    """Mapeamento da entidade de dominio Busca para a tabela 'buscas'."""

    __tablename__ = "buscas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    apelido: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)