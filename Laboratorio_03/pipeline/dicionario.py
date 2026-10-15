"""Dicionário de dados: ``python -m pipeline.dicionario``.

Confere se ``resultados/dicionario_dados.csv`` documenta exatamente as colunas
que o código gera e escreve ``resultados/dicionario_dados.md`` a partir dele
(o CSV é a fonte única; o .md não deve ser editado à mão).
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

from pipeline.arquivos import ler_csv
from pipeline.consolidar import COLUNAS_DATASET
from pipeline.exportar import COLUNAS_AMOSTRA, COLUNAS_COMMITS, COLUNAS_RELEASES, COLUNAS_RUNS
from validacao.amostra_ouro import COLUNAS_PLANILHA_RELEASES, COLUNAS_PLANILHA_REPOS
from validacao.avaliar_heuristica import COLUNAS_ERROS, COLUNAS_VERSOES
from validacao.concordancia import COLUNAS_CONCORDANCIA, COLUNAS_DIVERGENCIAS
from validacao.consenso import COLUNAS_CONSENSO, COLUNAS_DECISOES

CAMPOS_DICIONARIO = ["arquivo", "campo", "tipo", "unidade", "origem", "formula", "quando_vazio"]

ESQUEMAS = {
    "resultados/dataset_final.csv": COLUNAS_DATASET,
    "resultados/amostra_final.csv": COLUNAS_AMOSTRA,
    "resultados/funil_selecao.csv": ["etapa", "quantidade"],
    "resultados/releases_janela.csv": COLUNAS_RELEASES,
    "resultados/commits_releases.csv.gz": COLUNAS_COMMITS,
    "resultados/runs.csv.gz": COLUNAS_RUNS,
    "validacao/amostra_ouro_repositorios.csv": ["repositorio"],
    "validacao/amostra_ouro_releases.csv": ["repositorio", "tag", "tag_anterior", "published_at",
                                            "url_release", "url_compare"],
    "validacao/rotulos/rotulos_<avaliador>_repositorios.csv": COLUNAS_PLANILHA_REPOS,
    "validacao/rotulos/rotulos_<avaliador>_releases.csv": COLUNAS_PLANILHA_RELEASES,
    "validacao/concordancia.csv": COLUNAS_CONCORDANCIA,
    "validacao/divergencias.csv": COLUNAS_DIVERGENCIAS,
    "validacao/decisoes_reuniao.csv": COLUNAS_DECISOES,
    "validacao/consenso_repositorios.csv": COLUNAS_CONSENSO["repositorios"],
    "validacao/consenso_releases.csv": COLUNAS_CONSENSO["releases"],
    "validacao/heuristica_versoes.csv": COLUNAS_VERSOES,
    "validacao/erros_heuristica_<versao>.csv": COLUNAS_ERROS,
}


def verificar(dicionario):
    """Lista campos gerados pelo código sem documentação e entradas do
    dicionário que não existem no código."""
    documentados = defaultdict(set)
    for linha in dicionario:
        documentados[linha["arquivo"]].add(linha["campo"])
        incompletos = [c for c in ("tipo", "unidade", "origem", "formula") if not linha.get(c)]
        if incompletos:
            yield f"{linha['arquivo']} → {linha['campo']}: campos vazios {incompletos}"

    for arquivo, colunas in ESQUEMAS.items():
        for coluna in colunas:
            if coluna not in documentados[arquivo]:
                yield f"{arquivo} → {coluna}: não documentado"

    for arquivo, campos in documentados.items():
        if arquivo not in ESQUEMAS:
            yield f"{arquivo}: arquivo desconhecido no dicionário"
            continue
        for campo in campos - set(ESQUEMAS[arquivo]):
            yield f"{arquivo} → {campo}: documentado mas não gerado pelo código"


def escapar(texto):
    return str(texto).replace("|", "\\|").replace("\n", " ")


def gerar_markdown(dicionario):
    partes = ["# Dicionário de dados — Lab03\n",
              "Gerado por `python -m pipeline.dicionario` a partir de `dicionario_dados.csv`. "
              "Não edite este arquivo à mão.\n"]
    por_arquivo = defaultdict(list)
    for linha in dicionario:
        por_arquivo[linha["arquivo"]].append(linha)

    for arquivo in ESQUEMAS:
        if arquivo not in por_arquivo:
            continue
        partes.append(f"\n## `{arquivo}`\n")
        partes.append("| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |")
        partes.append("|---|---|---|---|---|---|")
        ordem = {c: i for i, c in enumerate(ESQUEMAS[arquivo])}
        for linha in sorted(por_arquivo[arquivo], key=lambda l: ordem.get(l["campo"], 999)):
            partes.append("| " + " | ".join(escapar(linha.get(c, "")) for c in
                                             ("campo", "tipo", "unidade", "origem", "formula", "quando_vazio")) + " |")
    return "\n".join(partes) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Confere e gera o dicionário de dados")
    parser.add_argument("--dicionario", default="resultados/dicionario_dados.csv")
    args = parser.parse_args()

    dicionario = ler_csv(args.dicionario)
    problemas = list(verificar(dicionario))
    if problemas:
        print("Dicionário inconsistente:\n- " + "\n- ".join(problemas))
        sys.exit(1)

    destino = Path(args.dicionario).with_suffix(".md")
    destino.write_text(gerar_markdown(dicionario), encoding="utf-8")
    print(f"Dicionário consistente ({len(dicionario)} campos). Gerado: {destino}")


if __name__ == "__main__":
    main()
