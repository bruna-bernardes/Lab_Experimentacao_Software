
import csv
from unittest.mock import patch
from pipeline.__main__ import salvar_csv


def test_salvar_csv_com_bloqueio_temporario(tmp_path):
    caminho = tmp_path / "resultado.csv"
    dados = [{"repositorio": "exemplo/teste"}]

    from os import replace
    chamadas = 0

    def substituir(origem, destino):
        nonlocal chamadas
        chamadas += 1

        if chamadas == 1:
            raise PermissionError("Arquivo temporariamente bloqueado")

        return replace(origem, destino)

    with patch("pipeline.__main__.os.replace", side_effect=substituir), \
         patch("pipeline.__main__.time.sleep") as espera:

        salvar_csv(caminho, dados, ["repositorio"])

    assert chamadas == 2
    espera.assert_called_once_with(1)

    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        registros = list(csv.DictReader(arquivo))

    assert registros == dados
