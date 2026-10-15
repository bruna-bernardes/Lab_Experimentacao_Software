"""Leitura e escrita de CSV (simples ou .gz) de forma determinística."""
import csv
import gzip
import io
import os
from pathlib import Path


def escrever_csv(caminho, linhas, colunas):
    """Escreve CSV ordenado e reprodutível. Arquivos ``.gz`` são gerados com
    ``mtime=0`` para que duas execuções produzam bytes idênticos."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")

    texto = io.StringIO(newline="")
    escritor = csv.DictWriter(texto, fieldnames=colunas, extrasaction="ignore", lineterminator="\n")
    escritor.writeheader()
    for linha in linhas:
        escritor.writerow({c: formatar(linha.get(c)) for c in colunas})

    if caminho.suffix == ".gz":
        with open(temporario, "wb") as bruto:
            with gzip.GzipFile(filename="", mode="wb", fileobj=bruto, mtime=0) as compactado:
                compactado.write(texto.getvalue().encode("utf-8"))
    else:
        with open(temporario, "w", encoding="utf-8-sig", newline="") as arquivo:
            arquivo.write(texto.getvalue())

    os.replace(temporario, caminho)


def formatar(valor):
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    return valor


def ler_csv(caminho):
    caminho = Path(caminho)
    if caminho.suffix == ".gz":
        with gzip.open(caminho, "rt", encoding="utf-8-sig", newline="") as arquivo:
            return list(csv.DictReader(arquivo))

    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def booleano(valor):
    return str(valor).strip().lower() in ("true", "1", "sim", "yes")


def numero(valor):
    if valor is None or str(valor).strip() == "":
        return None
    valor = float(valor)
    return int(valor) if valor.is_integer() else valor
