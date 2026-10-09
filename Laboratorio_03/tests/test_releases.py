
from metricas import lead_time_por_release, lead_time_por_commit
from pipeline.releases import coletar_releases
from unittest.mock import Mock
from pipeline.releases import coletar_commits
from pipeline.releases import coletar_dados_releases
from requests.exceptions import HTTPError
from unittest.mock import patch


def criar_commit(data):
    return {"commit": {"author": {"date": data}}}


def test_lead_time_por_release():
    releases = [{
        "published_at": "2026-03-15T00:00:00Z",
        "commits": [
            criar_commit("2026-03-02T00:00:00Z"),
            criar_commit("2026-03-10T00:00:00Z"),
            criar_commit("2026-03-14T00:00:00Z")
        ]
    }]

    assert lead_time_por_release(releases) == 312


def test_lead_time_por_commit():
    releases = [{
        "published_at": "2026-03-15T00:00:00Z",
        "commits": [
            criar_commit("2026-03-02T00:00:00Z"),
            criar_commit("2026-03-10T00:00:00Z"),
            criar_commit("2026-03-14T00:00:00Z")
        ]
    }]

    assert lead_time_por_commit(releases) == 120


def test_release_sem_commits():
    releases = [{"published_at": "2026-03-15T00:00:00Z", "commits": []}]

    assert lead_time_por_release(releases) is None
    assert lead_time_por_commit(releases) is None


def test_coletar_releases():
    api = Mock()
    api.paginas.return_value = [
        {"tag_name": "v1", "draft": False, "prerelease": False,
         "published_at": "2026-03-10T00:00:00Z"},
        {"tag_name": "v2", "draft": True, "prerelease": False,
         "published_at": "2026-03-12T00:00:00Z"},
        {"tag_name": "v3", "draft": False, "prerelease": True,
         "published_at": "2026-03-13T00:00:00Z"}
    ]

    resultado = coletar_releases(
        api, "usuario/repositorio",
        "2026-03-01T00:00:00Z",
        "2026-03-31T23:59:59Z"
    )

    assert len(resultado) == 1
    assert resultado[0]["tag_name"] == "v1"

def test_paginacao_commits():
    api = Mock()
    primeira_pagina = [{"sha": str(i)} for i in range(100)]
    segunda_pagina = [{"sha": str(i)} for i in range(100, 125)]

    api.get.side_effect = [
        {"data": {"commits": primeira_pagina}},
        {"data": {"commits": segunda_pagina}}
    ]

    commits = coletar_commits(api, "usuario/repositorio", "v1", "v2")

    assert len(commits) == 125
    assert api.get.call_count == 2
    
def test_release_anterior_a_janela():
    api = Mock()
    api.paginas.return_value = [
        {
            "tag_name": "v1.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2025-12-20T00:00:00Z"
        },
        {
            "tag_name": "v1.1",
            "draft": False,
            "prerelease": False,
            "published_at": "2026-01-15T00:00:00Z"
        }
    ]

    api.get.return_value = {
        "data": {
            "commits": [
                {"sha": "abc123", "commit": {"author": {"date": "2026-01-10T00:00:00Z"}}}
            ]
        }
    }

    resultado, ignoradas = coletar_dados_releases(
        api, "usuario/repositorio",
        "2026-01-01T00:00:00Z",
        "2026-12-31T23:59:59Z"
    )

    assert len(resultado) == 1
    assert resultado[0]["tag_anterior"] == "v1.0"
    assert resultado[0]["tag"] == "v1.1"
    assert len(resultado[0]["commits"]) == 1
    assert ignoradas == 0

def test_comparacao_http_422():
    api = Mock()
    api.paginas.return_value = [
        {"tag_name": "v1", "draft": False, "prerelease": False,
         "published_at": "2025-12-20T00:00:00Z"},
        {"tag_name": "v2", "draft": False, "prerelease": False,
         "published_at": "2026-01-15T00:00:00Z"}
    ]

    resposta = Mock()
    resposta.status_code = 422
    erro = HTTPError("422 Unprocessable Entity", response=resposta)

    with patch("pipeline.releases.coletar_commits", side_effect=erro):
        resultado, ignoradas = coletar_dados_releases(
            api, "usuario/repositorio",
            "2026-01-01T00:00:00Z",
            "2026-12-31T23:59:59Z"
        )

    assert resultado == []
    assert ignoradas == 1
