"""Testes das rotas do painel web (TestClient com repositorio fake)."""

from fastapi.testclient import TestClient

from presentation.app import app, get_busca_repository


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