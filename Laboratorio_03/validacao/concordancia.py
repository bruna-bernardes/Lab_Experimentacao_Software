"""Concordância entre os três avaliadores (kappa de Fleiss):
``python -m validacao.concordancia``.

1. Valida os arquivos de rótulos (mesmos itens, sem vazios, vocabulário do
   guia de rotulagem).
2. Calcula, para cada dimensão — tipo do projeto, entregas reais e release
   corretiva —, o kappa de Fleiss com ``aggregate_raters`` + ``fleiss_kappa``
   do statsmodels, além da concordância bruta.
3. Lista os itens sem unanimidade em ``validacao/divergencias.csv``.
"""
import argparse
import math
from itertools import combinations
from pathlib import Path

import numpy as np
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

from validacao.comum import (
    AVALIADORES, NIVEIS, VOCABULARIO, arquivo_rotulos, ler_tabela, normalizar_rotulo
)
from pipeline.arquivos import escrever_csv

COLUNAS_CONCORDANCIA = ["dimensao", "nivel", "n_itens", "n_avaliadores", "n_categorias_usadas",
                        "kappa_fleiss", "interpretacao", "concordancia_unanime", "concordancia_pares"]

COLUNAS_DIVERGENCIAS = ["nivel", "repositorio", "tag", "dimensao"] + [f"rotulo_{a}" for a in AVALIADORES] + ["padrao"]


class RotulosInvalidos(ValueError):
    pass


def interpretar_kappa(kappa):
    """Faixas de Landis & Koch (1977)."""
    if kappa is None or (isinstance(kappa, float) and math.isnan(kappa)):
        return "indefinido"
    if kappa < 0:
        return "pobre"
    if kappa <= 0.20:
        return "leve"
    if kappa <= 0.40:
        return "razoavel"
    if kappa <= 0.60:
        return "moderada"
    if kappa <= 0.80:
        return "substancial"
    return "quase perfeita"


def chave_item(linha, campos):
    return tuple(linha.get(c, "") for c in campos)


def carregar_nivel(pasta, nivel, avaliadores=AVALIADORES):
    """Devolve ``{avaliador: {chave_item: {dimensao: rotulo}}}`` e levanta
    ``RotulosInvalidos`` com todos os problemas encontrados."""
    campos_chave, dimensoes = NIVEIS[nivel]
    problemas, rotulos = [], {}

    for avaliador in avaliadores:
        caminho = arquivo_rotulos(pasta, avaliador, nivel)
        if not caminho.exists():
            problemas.append(f"{caminho}: arquivo não encontrado")
            continue

        itens = {}
        for numero, linha in enumerate(ler_tabela(caminho), start=2):
            chave = chave_item(linha, campos_chave)
            if chave in itens:
                problemas.append(f"{caminho}:{numero}: item duplicado {chave}")
            valores = {}
            for dimensao in dimensoes:
                valor = normalizar_rotulo(linha.get(dimensao))
                if not valor:
                    problemas.append(f"{caminho}:{numero}: '{dimensao}' vazio em {chave}")
                elif valor not in VOCABULARIO[dimensao]:
                    problemas.append(f"{caminho}:{numero}: '{dimensao}' = '{linha.get(dimensao)}' "
                                     f"fora do vocabulário {VOCABULARIO[dimensao]}")
                valores[dimensao] = valor
            itens[chave] = valores
        rotulos[avaliador] = itens

    if len(rotulos) == len(avaliadores):
        referencia = set(rotulos[avaliadores[0]])
        for avaliador in avaliadores[1:]:
            faltando = referencia - set(rotulos[avaliador])
            sobrando = set(rotulos[avaliador]) - referencia
            if faltando:
                problemas.append(f"{avaliador} ({nivel}): faltam {len(faltando)} itens, ex.: {sorted(faltando)[:3]}")
            if sobrando:
                problemas.append(f"{avaliador} ({nivel}): {len(sobrando)} itens extras, ex.: {sorted(sobrando)[:3]}")

    if problemas:
        raise RotulosInvalidos("Rótulos inválidos:\n- " + "\n- ".join(problemas))

    return rotulos


def matriz(rotulos, dimensao, avaliadores=AVALIADORES):
    itens = sorted(rotulos[avaliadores[0]])
    return itens, [[rotulos[a][item][dimensao] for a in avaliadores] for item in itens]


def kappa_fleiss(linhas):
    tabela, _ = aggregate_raters(np.array(linhas, dtype=object))
    with np.errstate(divide="ignore", invalid="ignore"):
        valor = float(fleiss_kappa(tabela, method="fleiss"))
    return None if math.isnan(valor) else valor


def concordancia_bruta(linhas):
    unanime = sum(len(set(l)) == 1 for l in linhas) / len(linhas)
    pares = [a == b for l in linhas for a, b in combinations(l, 2)]
    return unanime, sum(pares) / len(pares)


def padrao(linha):
    contagem = sorted((linha.count(v) for v in set(linha)), reverse=True)
    return "-".join(str(c) for c in contagem)


def calcular(pasta_rotulos, avaliadores=AVALIADORES):
    resultados, divergencias = [], []

    for nivel, (campos_chave, dimensoes) in NIVEIS.items():
        rotulos = carregar_nivel(pasta_rotulos, nivel, avaliadores)
        for dimensao in dimensoes:
            itens, linhas = matriz(rotulos, dimensao, avaliadores)
            if not linhas:
                continue
            kappa = kappa_fleiss(linhas)
            unanime, pares = concordancia_bruta(linhas)
            resultados.append({
                "dimensao": dimensao, "nivel": nivel, "n_itens": len(linhas),
                "n_avaliadores": len(avaliadores),
                "n_categorias_usadas": len({v for l in linhas for v in l}),
                "kappa_fleiss": None if kappa is None else round(kappa, 4),
                "interpretacao": interpretar_kappa(kappa),
                "concordancia_unanime": round(unanime, 4),
                "concordancia_pares": round(pares, 4),
            })
            for item, linha in zip(itens, linhas):
                if len(set(linha)) > 1:
                    registro = dict(zip(campos_chave, item))
                    divergencias.append({
                        "nivel": nivel, "repositorio": registro["repositorio"],
                        "tag": registro.get("tag", ""), "dimensao": dimensao,
                        **{f"rotulo_{a}": v for a, v in zip(avaliadores, linha)},
                        "padrao": padrao(linha),
                    })

    return resultados, divergencias


def executar(validacao="validacao"):
    validacao = Path(validacao)
    resultados, divergencias = calcular(validacao / "rotulos")

    escrever_csv(validacao / "concordancia.csv", resultados, COLUNAS_CONCORDANCIA)
    escrever_csv(validacao / "divergencias.csv", divergencias, COLUNAS_DIVERGENCIAS)

    for r in resultados:
        print(f"{r['dimensao']:>15}: kappa = {r['kappa_fleiss']} ({r['interpretacao']}), "
              f"n = {r['n_itens']}, unânime = {r['concordancia_unanime']:.1%}")
    print(f"Itens divergentes: {len(divergencias)} → {validacao / 'divergencias.csv'}")
    return resultados, divergencias


def main():
    parser = argparse.ArgumentParser(description="Kappa de Fleiss entre os avaliadores")
    parser.add_argument("--validacao", default="validacao")
    parser.add_argument("--somente-validar", action="store_true",
                        help="apenas confere os arquivos de rótulos")
    args = parser.parse_args()

    if args.somente_validar:
        for nivel in NIVEIS:
            carregar_nivel(Path(args.validacao) / "rotulos", nivel)
        print("Arquivos de rótulos válidos.")
        return

    executar(args.validacao)


if __name__ == "__main__":
    main()
