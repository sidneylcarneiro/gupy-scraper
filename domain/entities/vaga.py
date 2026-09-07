"""Entidade de dominio que representa uma vaga extraida da Gupy.

Regras de negocio puras, sem dependencia de framework ou infraestrutura (Clean Architecture / DDD.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class FormatoTrabalho(Enum):
    """Formatos de trabalho possiveis para uma vaga."""

    HIBRIDO = "Hibrido"
    PRESENCIAL = "Presencial"
    REMOTO = "Remoto"


class StatusVaga(Enum):
    """Status do ciclo de vida de uma vaga no funil de candidaturas."""

    ATIVA = "Ativa"
    CANDIDATURA_ENVIADA = "Candidatura Enviada"
    EM_ANDAMENTO = "Em andamento"
    REJEITADA = "Rejeitada"
    CONTRATADA = "Contratada"


@dataclass
class Vaga:

    """Modela uma vaga de emprego capturada da plataforma Gupy."""

    titulo: str
    empresa: str
    localizacao: str
    formato: FormatoTrabalho
    descricao: str
    url: str
    id: Optional[int] = None
    data_publicacao: Optional[datetime] = None
    status: StatusVaga = StatusVaga.ATIVA


    @property
    def slug(self) -> str:
        """Identificador textual curto para a vaga (ex.: uso em rotas/URIs)."""
        base = f"{self.empresa}-{self.titulo}".lower()
        return base.replace(" ", "-")