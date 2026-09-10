import importlib.util
from pathlib import Path

CAMINHO_SOLUCAO = Path(__file__).parent / "solucao.py"
SPEC = importlib.util.spec_from_file_location("solucao_kata_04", CAMINHO_SOLUCAO)
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)

import pytest

avaliar_sla = MODULO.avaliar_sla


def test_prioridade_baixa_dentro():
    assert avaliar_sla("baixa", 10) == {
        "prazo_horas": 72.0,
        "status": "DENTRO",
    }


def test_prioridade_media_atencao():
    assert avaliar_sla("media", 40) == {
        "prazo_horas": 48.0,
        "status": "ATENCAO",
    }


def test_prioridade_alta_estourada():
    assert avaliar_sla("alta", 25) == {
        "prazo_horas": 24.0,
        "status": "ESTOURADO",
    }


def test_prioridade_critica_no_limite_de_atencao():
    assert avaliar_sla("critica", 6) == {
        "prazo_horas": 8.0,
        "status": "ATENCAO",
    }


def test_prioridade_sem_diferenca_de_maiusculas():
    assert avaliar_sla("CRITICA", 5) == {
        "prazo_horas": 8.0,
        "status": "DENTRO",
    }


def test_cliente_vip_reduz_prazo():
    assert avaliar_sla("media", 20, cliente_vip=True) == {
        "prazo_horas": 36.0,
        "status": "DENTRO",
    }


def test_cliente_vip_em_atencao():
    assert avaliar_sla("alta", 14, cliente_vip=True) == {
        "prazo_horas": 18.0,
        "status": "ATENCAO",
    }


def test_indisponibilidade_total():
    assert avaliar_sla(
        "baixa", 3, indisponibilidade_total=True
    ) == {
        "prazo_horas": 4.0,
        "status": "ATENCAO",
    }


def test_indisponibilidade_total_estourada():
    assert avaliar_sla(
        "critica",
        4.1,
        cliente_vip=True,
        indisponibilidade_total=True,
    ) == {
        "prazo_horas": 4.0,
        "status": "ESTOURADO",
    }


def test_dados_invalidos():
    with pytest.raises(ValueError):
        avaliar_sla("urgente", 2)

    with pytest.raises(ValueError):
        avaliar_sla("baixa", -1)
