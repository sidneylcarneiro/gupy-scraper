"""Adaptador PostgreSQL do contrato IVagaRepository (camada de infraestrutura)."""

from typing import Optional

from sqlalchemy.orm import Session

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga
from domain.repositories.vaga_repository import IVagaRepository
from infrastructure.database.models import VagaModel


def _para_modelo(vaga: Vaga) -> VagaModel:
    """Converte a entidade de dominio para o modelo ORM."""
    return VagaModel(
        id=vaga.id,
        titulo=vaga.titulo,
        empresa=vaga.empresa,
        localizacao=vaga.localizacao,
        formato=vaga.formato,
        descricao=vaga.descricao,
        url=vaga.url,
        data_publicacao=vaga.data_publicacao,
        status=vaga.status,
    )


def _para_entidade(modelo: VagaModel) -> Vaga:
    """Converte o modelo ORM para a entidade de dominio."""
    return Vaga(
        id=modelo.id,
        titulo=modelo.titulo,
        empresa=modelo.empresa,
        localizacao=modelo.localizacao,
        formato=FormatoTrabalho(modelo.formato),
        descricao=modelo.descricao,
        url=modelo.url,
        data_publicacao=modelo.data_publicacao,
        status=StatusVaga(modelo.status),
    )


def _atualizar_modelo(modelo: VagaModel, vaga: Vaga) -> None:
    """Copia os campos da entidade para o modelo ja persistido (preserva id/url)."""
    modelo.titulo = vaga.titulo
    modelo.empresa = vaga.empresa
    modelo.localizacao = vaga.localizacao
    modelo.formato = vaga.formato
    modelo.descricao = vaga.descricao
    modelo.data_publicacao = vaga.data_publicacao
    modelo.status = vaga.status


class PostgresVagaRepository(IVagaRepository):
    """Implementa a persistencia de vagas em PostgreSQL via SQLAlchemy."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def salvar(self, vaga: Vaga) -> None:
        """Insere a vaga ou atualiza a existente quando a URL ja consta (upsert).

        A coluna url e unica na tabela `vagas`; o upsert mantem o pipeline
        re-executavel sem violar a constraint e sem duplicar registros.
        """
        session: Session = self._session_factory()
        try:
            modelo = session.query(VagaModel).filter(VagaModel.url == vaga.url).one_or_none()
            if modelo is None:
                session.add(_para_modelo(vaga))
            else:
                _atualizar_modelo(modelo, vaga)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def buscar_por_url(self, url: str) -> Optional[Vaga]:
        session: Session = self._session_factory()
        try:
            modelo = session.query(VagaModel).filter(VagaModel.url == url).one_or_none()
            if modelo is None:
                return None
            return _para_entidade(modelo)
        finally:
            session.close()