
import pytest
from metricas import calcular_cfr_ci, calcular_recuperacao
from pipeline.workflows import periodos_mensais
from unittest.mock import Mock
from pipeline.workflows import coletar_runs


def test_cfr_ci():
    runs = [
        {"conclusion": "success"},
        {"conclusion": "failure"},
        {"conclusion": "timed_out"},
        {"conclusion": "cancelled"}
    ]

    assert calcular_cfr_ci(runs) == pytest.approx(2 / 3)


def test_cfr_sem_runs_validas():
    assert calcular_cfr_ci([{"conclusion": "cancelled"}]) is None


def test_tempo_recuperacao():
    runs = [
        {"workflow_id": 1, "conclusion": "success",
         "run_started_at": "2026-01-01T09:00:00Z",
         "updated_at": "2026-01-01T09:05:00Z"},
        {"workflow_id": 1, "conclusion": "failure",
         "run_started_at": "2026-01-01T10:00:00Z",
         "updated_at": "2026-01-01T10:05:00Z"},
        {"workflow_id": 1, "conclusion": "failure",
         "run_started_at": "2026-01-01T10:30:00Z",
         "updated_at": "2026-01-01T10:35:00Z"},
        {"workflow_id": 1, "conclusion": "success",
         "run_started_at": "2026-01-01T11:15:00Z",
         "updated_at": "2026-01-01T11:20:00Z"}
    ]

    resultado = calcular_recuperacao(runs)

    assert resultado["mediana_horas"] == pytest.approx(80 / 60)
    assert resultado["episodios_recuperados"] == 1
    assert resultado["episodios_censurados"] == 0


def test_recuperacao_censurada():
    runs = [
        {"workflow_id": 1, "conclusion": "success",
         "run_started_at": "2026-01-01T09:00:00Z",
         "updated_at": "2026-01-01T09:05:00Z"},
        {"workflow_id": 1, "conclusion": "failure",
         "run_started_at": "2026-01-01T10:00:00Z",
         "updated_at": "2026-01-01T10:05:00Z"}
    ]

    resultado = calcular_recuperacao(runs)

    assert resultado["episodios_recuperados"] == 0
    assert resultado["episodios_censurados"] == 1
    assert resultado["proporcao_censura"] == 1

def test_periodos_mensais():
    periodos = list(periodos_mensais(
        "2026-01-15T00:00:00Z",
        "2026-03-10T23:59:59Z"
    ))

    assert len(periodos) == 3

    assert periodos[0][0].day == 15
    assert periodos[0][1].day == 31

    assert periodos[1][0].month == 2
    assert periodos[1][1].day == 28

    assert periodos[2][0].month == 3
    assert periodos[2][1].day == 10

def test_subdivisao_automatica():
    api = Mock()

    def resposta(endpoint, params):
        periodo = params["created"]
        pagina = params["page"]

        if periodo == "2026-01-01T00:00:00Z..2026-01-02T23:59:59Z":
            return {"data": {"total_count": 1200, "workflow_runs": []}}

        if pagina > 1:
            return {"data": {"total_count": 1, "workflow_runs": []}}

        inicio = periodo.split("..")[0]
        identificador = 1 if inicio.startswith("2026-01-01") else 2

        return {"data": {
            "total_count": 1,
            "workflow_runs": [{
                "id": identificador,
                "head_branch": "main",
                "event": "push",
                "created_at": inicio,
                "conclusion": "success"
            }]
        }}

    api.get.side_effect = resposta

    runs = coletar_runs(
        api, "usuario/repositorio", "main",
        "2026-01-01T00:00:00Z",
        "2026-01-02T23:59:59Z"
    )

    assert len(runs) == 2
    assert len({run["id"] for run in runs}) == 2
    assert api.get.call_count == 3