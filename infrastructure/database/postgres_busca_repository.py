"""Repositorio PostgreSQL de buscas salvas (implementa IBuscaRepository)."""

from typing import Optional

from sqlalchemy.exc import IntegrityError

from domain.entities.busca import Busca
from domain.repositories.busca_repository import IBuscaRepository
from infrastructure.database.models import BuscaModel


class ApelidoJaExisteError(Exception):
    """Sinaliza que ja existe uma busca com o mesmo apelido."""


class PostgresBuscaRepository(IBuscaRepository):
    """Adaptador PostgreSQL para o port IBuscaRepository."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def salvar(self, busca: Busca) -> Busca:
        """Insere a busca e retorna a entidade persistida (com id)."""
        session = self._session_factory()
        try:
            modelo = BuscaModel(apelido=busca.apelido, url=busca.url)
            session.add(modelo)
            session.commit()
            return Busca(id=modelo.id, apelido=modelo.apelido, url=modelo.url)
        except IntegrityError as erro:
            session.rollback()
            raise ApelidoJaExisteError(f"Ja existe uma busca com o apelido '{busca.apelido}'.") from erro
        finally:
            session.close()

    def listar(self) -> list[Busca]:
        """Retorna todas as buscas ordenadas por apelido."""
        session = self._session_factory()
        try:
            modelos = session.query(BuscaModel).order_by(BuscaModel.apelido).all()
            return [self._para_entidade(modelo) for modelo in modelos]
        finally:
            session.close()

    def buscar_por_id(self, id_busca: int) -> Optional[Busca]:
        """Busca pelo id; retorna None quando nao encontrada."""
        session = self._session_factory()
        try:
            modelo = session.get(BuscaModel, id_busca)
            return self._para_entidade(modelo) if modelo is not None else None
        finally:
            session.close()

    def remover(self, id_busca: int) -> None:
        """Remove a busca pelo id (sem erro se nao existir)."""
        session = self._session_factory()
        try:
            modelo = session.get(BuscaModel, id_busca)
            if modelo is not None:
                session.delete(modelo)
                session.commit()
        finally:
            session.close()

    @staticmethod
    def _para_entidade(modelo: BuscaModel) -> Busca:
        return Busca(id=modelo.id, apelido=modelo.apelido, url=modelo.url)