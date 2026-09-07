"""Entidade de dominio: busca salva (URL de pesquisa da Gupy com apelido)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Busca:
    """Representa uma URL de busca da Gupy nomeada pelo usuario."""

    apelido: str
    url: str
    id: Optional[int] = None