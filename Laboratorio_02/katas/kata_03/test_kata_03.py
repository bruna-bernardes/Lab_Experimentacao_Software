import importlib.util
from pathlib import Path

CAMINHO_SOLUCAO = Path(__file__).parent / "solucao.py"
SPEC = importlib.util.spec_from_file_location("solucao_kata_03", CAMINHO_SOLUCAO)
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)

import pytest

calcular_total_pedido = MODULO.calcular_total_pedido


def test_pedido_basico_com_frete():
    itens = [{"preco": 50.00, "quantidade": 1}]
    assert calcular_total_pedido(itens) == 65.00


def test_varios_itens():
    itens = [
        {"preco": 30.00, "quantidade": 2},
        {"preco": 20.00, "quantidade": 1},
    ]
    assert calcular_total_pedido(itens) == 95.00


def test_frete_gratis_por_subtotal():
    itens = [{"preco": 75.00, "quantidade": 2}]
    assert calcular_total_pedido(itens) == 150.00


def test_retirada_sem_frete():
    itens = [{"preco": 50.00, "quantidade": 1}]
    assert calcular_total_pedido(itens, retirada=True) == 50.00


def test_desc10_sem_subtotal_minimo():
    itens = [{"preco": 80.00, "quantidade": 1}]
    assert calcular_total_pedido(itens, cupom="DESC10") == 95.00


def test_desc10_com_subtotal_minimo():
    itens = [{"preco": 100.00, "quantidade": 1}]
    assert calcular_total_pedido(itens, cupom="DESC10") == 105.00


def test_desc20():
    itens = [{"preco": 250.00, "quantidade": 1}]
    assert calcular_total_pedido(itens, cupom="DESC20") == 200.00


def test_cliente_vip():
    itens = [{"preco": 100.00, "quantidade": 1}]
    assert calcular_total_pedido(itens, cliente_vip=True) == 110.00


def test_cupom_e_vip_cumulativos():
    itens = [{"preco": 100.00, "quantidade": 1}]
    assert calcular_total_pedido(
        itens, cupom="DESC10", cliente_vip=True
    ) == 100.50


def test_itens_invalidos():
    with pytest.raises(ValueError):
        calcular_total_pedido([])

    with pytest.raises(ValueError):
        calcular_total_pedido([{"preco": 0, "quantidade": 1}])

    with pytest.raises(ValueError):
        calcular_total_pedido([{"preco": 10, "quantidade": 0}])
