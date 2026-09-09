import importlib.util
from pathlib import Path

CAMINHO_SOLUCAO = Path(__file__).parent / "solucao.py"
SPEC = importlib.util.spec_from_file_location("solucao_kata_02", CAMINHO_SOLUCAO)
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)

import pytest

calcular_estacionamento = MODULO.calcular_estacionamento


def test_ate_30_minutos():
    assert calcular_estacionamento(20) == 4.00


def test_de_31_a_60_minutos():
    assert calcular_estacionamento(45) == 7.00


def test_primeiro_bloco_adicional():
    assert calcular_estacionamento(61) == 10.00


def test_um_bloco_adicional_completo():
    assert calcular_estacionamento(90) == 10.00


def test_segundo_bloco_adicional_iniciado():
    assert calcular_estacionamento(91) == 13.00


def test_limite_diario():
    assert calcular_estacionamento(600) == 35.00


def test_fim_de_semana():
    assert calcular_estacionamento(60, fim_de_semana=True) == 8.40


def test_mensalista():
    assert calcular_estacionamento(60, mensalista=True) == 5.25


def test_fim_de_semana_e_mensalista():
    assert calcular_estacionamento(
        60, fim_de_semana=True, mensalista=True
    ) == 6.30


def test_minutos_invalidos():
    with pytest.raises(ValueError):
        calcular_estacionamento(0)

    with pytest.raises(ValueError):
        calcular_estacionamento(1441)
