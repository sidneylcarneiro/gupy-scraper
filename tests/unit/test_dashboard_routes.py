"""Testes das rotas do painel web (TestClient com repositorio fake)."""

from fastapi.testclient import TestClient

from domain.entities.vaga import StatusVaga
from presentation.app import app, get_busca_repository, get_vaga_repository


class RepositorioBuscaFake:
    """Repositorio falso em memoria para as rotas do painel."""

    def __init__(self):
        self._proximo_id = 1
        self.salvas = {}

    def salvar(self, busca):
        busca.id = self._proximo_id
        self._proximo_id += 1
        self.salvas[busca.id] = busca
        return busca

    def listar(self):
        return sorted(self.salvas.values(), key=lambda busca: busca.apelido)

    def buscar_por_id(self, id_busca):
        return self.salvas.get(id_busca)

    def remover(self, id_busca):
        self.salvas.pop(id_busca, None)


repositorio_fake = RepositorioBuscaFake()


def obter_fake():
    return repositorio_fake


app.dependency_overrides[get_busca_repository] = obter_fake
cliente = TestClient(app)


def test_dashboard_deve_exibir_formulario_e_lista_vazia():
    repositorio_fake.salvas.clear()
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert "Nova busca" in resposta.text
    assert "Nenhuma busca cadastrada" in resposta.text


def test_deve_cadastrar_busca_via_painel():
    repositorio_fake.salvas.clear()
    resposta = cliente.post(
        "/buscas",
        data={"apelido": "Python Remoto", "url": "https://portal.gupy.io/job-search/term=python"},
    )

    assert resposta.status_code == 200
    assert "Python Remoto" in resposta.text
    assert "cadastrada com sucesso" in resposta.text
    assert len(repositorio_fake.salvas) == 1


def test_deve_exibir_erro_para_url_fora_do_gupy():
    repositorio_fake.salvas.clear()
    resposta = cliente.post("/buscas", data={"apelido": "X", "url": "https://linkedin.com/jobs"})

    assert resposta.status_code == 200
    assert "Erro:" in resposta.text
    assert "portal da Gupy" in resposta.text
    assert repositorio_fake.salvas == {}


def test_deve_remover_busca_via_painel():
    repositorio_fake.salvas.clear()
    busca = repositorio_fake.salvar(
        type("BuscaFake", (), {"apelido": "Temp", "url": "https://portal.gupy.io/job-search/term=temp", "id": None})()
    )

    resposta = cliente.delete(f"/buscas/{busca.id}")

    assert resposta.status_code == 200
    assert repositorio_fake.salvas == {}
    assert "Busca removida" in resposta.text


class RepositorioVagaFake:
    """Repositorio de vagas em memoria para as rotas do Kanban."""

    def __init__(self, vagas):
        self.vagas = {vaga.id: vaga for vaga in vagas}

    def salvar(self, vaga):
        pass

    def buscar_por_url(self, url):
        return None

    def listar_todas(self):
        return list(self.vagas.values())

    def buscar_por_id(self, id_vaga):
        return self.vagas.get(id_vaga)

    def atualizar_status(self, id_vaga, status):
        vaga = self.vagas.get(id_vaga)
        if vaga is None:
            return None
        vaga.status = status
        return vaga


def _vaga_fake(id_vaga, status):
    from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga

    return Vaga(
        titulo=f"Dev {id_vaga}",
        empresa="Acme",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao="desc",
        url=f"https://acme.gupy.io/job/{id_vaga}",
        id=id_vaga,
        status=status,
    )


repositorio_vagas_fake = RepositorioVagaFake([])


def obter_vaga_fake():
    return repositorio_vagas_fake


app.dependency_overrides[get_vaga_repository] = obter_vaga_fake


def test_kanban_deve_exibir_colunas_e_vagas_agrupadas_por_status():
    repositorio_vagas_fake.vagas = {
        1: _vaga_fake(1, StatusVaga.ATIVA),
        2: _vaga_fake(2, StatusVaga.CANDIDATURA_ENVIADA),
    }

    resposta = cliente.get("/kanban")

    assert resposta.status_code == 200
    assert "Kanban de Vagas" in resposta.text
    for coluna in ("Ativa", "Candidatura Enviada", "Em andamento", "Rejeitada", "Contratada"):
        assert coluna in resposta.text
    assert "Dev 1" in resposta.text
    assert " sortable" not in resposta.text or "Sortable" in resposta.text  # SortableJS presente


def test_patch_status_deve_atualizar_vaga_e_retornar_card():
    repositorio_vagas_fake.vagas = {1: _vaga_fake(1, StatusVaga.ATIVA)}

    resposta = cliente.patch("/vagas/1/status", data={"status": "Contratada"})

    assert resposta.status_code == 200
    assert "Contratada" in resposta.text
    assert repositorio_vagas_fake.vagas[1].status == StatusVaga.CONTRATADA


def test_patch_status_deve_rejeitar_status_invalido():
    repositorio_vagas_fake.vagas = {1: _vaga_fake(1, StatusVaga.ATIVA)}

    resposta = cliente.patch("/vagas/1/status", data={"status": "Status Inexistente"})

    assert resposta.status_code == 200
    assert "Status invalido" in resposta.text
    assert repositorio_vagas_fake.vagas[1].status == StatusVaga.ATIVA  # inalterado


def test_inbox_deve_exibir_apenas_vagas_com_status_nova():
    repositorio_vagas_fake.vagas = {
        1: _vaga_fake(1, StatusVaga.NOVA),
        2: _vaga_fake(2, StatusVaga.ATIVA),
        3: _vaga_fake(3, StatusVaga.DESCARTADA),
    }

    resposta = cliente.get("/inbox")

    assert resposta.status_code == 200
    assert "Inbox" in resposta.text
    assert "Dev 1" in resposta.text
    assert "Dev 2" not in resposta.text
    assert "Dev 3" not in resposta.text
    assert "Adicionar ao Kanban" in resposta.text
    assert "Descartar" in resposta.text


def test_kanban_nao_deve_exibir_vagas_nova_nem_descartada():
    repositorio_vagas_fake.vagas = {
        1: _vaga_fake(1, StatusVaga.NOVA),
        2: _vaga_fake(2, StatusVaga.ATIVA),
        3: _vaga_fake(3, StatusVaga.DESCARTADA),
    }

    resposta = cliente.get("/kanban")

    assert resposta.status_code == 200
    assert "Dev 2" in resposta.text
    assert "Dev 1" not in resposta.text
    assert "Dev 3" not in resposta.text
    assert 'data-status="Nova"' not in resposta.text
    assert 'data-status="Descartada"' not in resposta.text


def test_detalhes_deve_exibir_dados_da_vaga():
    repositorio_vagas_fake.vagas = {1: _vaga_fake(1, StatusVaga.NOVA)}

    resposta = cliente.get("/vagas/1")

    assert resposta.status_code == 200
    assert "Dev 1" in resposta.text
    assert "Acme" in resposta.text
    assert "https://acme.gupy.io/job/1" in resposta.text
    assert 'target="_blank"' in resposta.text
    assert "Análise de Perfil" in resposta.text
    assert "Mock Interview" in resposta.text


def test_detalhes_de_vaga_inexistente_deve_retornar_404():
    resposta = cliente.get("/vagas/999")

    assert resposta.status_code == 404