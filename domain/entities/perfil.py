"""Entidade de dominio: perfil do candidato."""

from dataclasses import dataclass


@dataclass
class PerfilCandidato:
    """Representa o candidato e sua experiencia professional resumida."""

    nome: str
    resumo_experiencia: str