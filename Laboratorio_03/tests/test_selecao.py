
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

# --- Sprint 2 (#A1) ---------------------------------------------------------
from pipeline.selecao import (
    montar_pool, ordenar_pool, candidatos, contar_contribuidores,
    info_repositorio, ultima_pagina, idade_em_dias
)
from requests.exceptions import HTTPError


def api_busca_falsa():
    """Busca falsa: cada faixa devolve dois repositórios próprios."""
    api = Mock()

    def resposta(endpoint, params):
        return {"data": {"total_count": 2}}

    def paginas(endpoint, params, limite):
        faixa = params["q"].split("stars:")[1].split(" ")[0]
        return [
            {"full_name": f"org/{faixa}-a", "stargazers_count": 1},
            {"full_name": f"org/{faixa}-b", "stargazers_count": 1},
        ]

    api.get.side_effect = resposta
    api.paginas.side_effect = paginas
    return api


def test_pool_cobre_todas_as_faixas():
    pool = montar_pool(api_busca_falsa())
    faixas = {r["repositorio"].split("/")[1].rsplit("-", 1)[0] for r in pool}

    assert faixas == {"1001..2000", "2001..5000", "5001..10000", "10001..1000000"}
    assert len(pool) == 8


def test_pool_sem_duplicados():
    api = Mock()
    api.get.return_value = {"data": {"total_count": 1}}
    api.paginas.return_value = [{"full_name": "org/mesmo", "stargazers_count": 1}]

    assert len(montar_pool(api)) == 1


def test_ordem_reprodutivel_com_mesma_semente():
    pool = montar_pool(api_busca_falsa())

    primeira = [r["repositorio"] for r in ordenar_pool([dict(r) for r in pool], 42)]
    segunda = [r["repositorio"] for r in ordenar_pool([dict(r) for r in reversed(pool)], 42)]
    outra = [r["repositorio"] for r in ordenar_pool([dict(r) for r in pool], 7)]

    assert primeira == segunda
    assert primeira != outra


def test_candidatos_com_semente_respeitam_maximo():
    resultado = list(candidatos(api_busca_falsa(), maximo=3, semente=42))

    assert len(resultado) == 3
    assert [r["ordem_pool"] for r in resultado] == [1, 2, 3]


def test_contribuidores_pelo_cabecalho_link():
    api = Mock()
    api.get.return_value = {
        "data": [{"login": "x"}],
        "headers": {"Link": '<https://api.github.com/repositories/1/contributors?per_page=1&anon=true&page=2>; rel="next", '
                            '<https://api.github.com/repositories/1/contributors?per_page=1&anon=true&page=37>; rel="last"'}
    }

    assert contar_contribuidores(api, "org/repo") == 37
    api.get.assert_called_once_with("/repos/org/repo/contributors", {"per_page": 1, "anon": "true"})


def test_contribuidores_sem_link():
    api = Mock()
    api.get.return_value = {"data": [{"login": "x"}], "headers": {}}

    assert contar_contribuidores(api, "org/repo") == 1


def test_contribuidores_lista_muito_grande():
    resposta = Mock()
    resposta.status_code = 403
    api = Mock()
    api.get.side_effect = HTTPError("403", response=resposta)

    assert contar_contribuidores(api, "org/enorme") is None


def test_ultima_pagina_sem_last():
    assert ultima_pagina(None) is None
    assert ultima_pagina('<https://x?page=2>; rel="next"') is None


def test_idade_relativa_ao_fim_da_janela():
    api = Mock()
    api.get.return_value = {"data": {
        "default_branch": "main", "stargazers_count": 1500,
        "language": "Python", "created_at": "2025-09-30T23:59:59Z"
    }}

    dados = info_repositorio(api, "org/repo", "2026-09-30T23:59:59Z")

    assert dados["idade_dias"] == 365
    assert dados["branch"] == "main"
    assert idade_em_dias("2026-01-01T00:00:00Z", "2026-01-11T00:00:00Z") == 10
