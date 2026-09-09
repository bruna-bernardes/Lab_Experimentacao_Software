import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from solucao import calcular_total


def test_lista_vazia():
    assert calcular_total([]) == 0


def test_um_valor():
    assert calcular_total([10]) == 10


def test_varios_valores():
    assert calcular_total([10, 20, 30]) == 60


def test_valores_decimais():
    assert calcular_total([5.5, 4.5]) == 10.0


def test_valores_negativos():
    assert calcular_total([10, -3, 2]) == 9
