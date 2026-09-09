import importlib.util
from pathlib import Path

CAMINHO_SOLUCAO = Path(__file__).parent / "solucao.py"
SPEC = importlib.util.spec_from_file_location("solucao_kata_01", CAMINHO_SOLUCAO)
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)

import pytest

calcular_tarifa_entrega = MODULO.calcular_tarifa_entrega


def test_tarifa_base():
    assert calcular_tarifa_entrega(1, 10) == 10.00


def test_acrescimo_peso_entre_2_e_5():
    assert calcular_tarifa_entrega(3, 10) == 14.00


def test_acrescimo_peso_entre_5_e_10():
    assert calcular_tarifa_entrega(7, 10) == 18.00


def test_acrescimo_peso_acima_de_10():
    assert calcular_tarifa_entrega(12, 10) == 25.00


def test_acrescimo_distancia_media():
    assert calcular_tarifa_entrega(1, 50) == 15.00


def test_acrescimo_distancia_longa():
    assert calcular_tarifa_entrega(1, 150) == 22.00


def test_peso_e_distancia_combinados():
    assert calcular_tarifa_entrega(7, 150) == 30.00


def test_entrega_expressa():
    assert calcular_tarifa_entrega(1, 10, expressa=True) == 15.00


def test_expressa_com_cliente_premium():
    assert calcular_tarifa_entrega(
        1, 10, expressa=True, cliente_premium=True
    ) == 13.50


def test_valores_invalidos():
    with pytest.raises(ValueError):
        calcular_tarifa_entrega(0, 10)

    with pytest.raises(ValueError):
        calcular_tarifa_entrega(1, 0)
