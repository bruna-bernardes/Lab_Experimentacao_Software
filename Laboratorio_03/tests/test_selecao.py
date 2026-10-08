
from unittest.mock import Mock, patch
from pipeline.selecao import selecionar_repositorios
from pipeline.selecao import buscar_faixa


def test_selecionar_repositorios():
    api = Mock()
    repos = [{"full_name": f"usuario/repo{i}"} for i in range(5)]

    with patch("pipeline.selecao.candidatos", return_value=iter(repos)), \
         patch("pipeline.selecao.possui_actions", side_effect=[False, True, False, True, True]), \
         patch("pipeline.selecao.metadados", side_effect=lambda api, repo: {"repositorio": repo["full_name"]}):

        selecionados, funil = selecionar_repositorios(api, quantidade=2)

    assert len(selecionados) == 2
    assert funil["candidatos"] == 4
    assert funil["com_actions"] == 2
    assert funil["sem_actions"] == 2


def test_nenhum_repositorio_com_actions():
    api = Mock()
    repos = [{"full_name": f"usuario/repo{i}"} for i in range(3)]

    with patch("pipeline.selecao.candidatos", return_value=iter(repos)), \
         patch("pipeline.selecao.possui_actions", return_value=False):

        selecionados, funil = selecionar_repositorios(api, quantidade=2)

    assert selecionados == []
    assert funil["candidatos"] == 3
    assert funil["com_actions"] == 0
    assert funil["sem_actions"] == 3

def test_divisao_faixas():
    api = Mock()

    def resposta(endpoint, params):
        faixa = params["q"].split("stars:")[1].split(" ")[0]
        total = 1500 if faixa == "1001..2000" else 1
        return {"data": {"total_count": total}}

    api.get.side_effect = resposta
    api.paginas.side_effect = lambda endpoint, params, limite: [
        {"full_name": params["q"].split("stars:")[1].split(" ")[0]}
    ]

    resultado = list(buscar_faixa(api, 1001, 2000))

    assert len(resultado) == 2
    assert api.get.call_count == 3
    assert api.paginas.call_count == 2