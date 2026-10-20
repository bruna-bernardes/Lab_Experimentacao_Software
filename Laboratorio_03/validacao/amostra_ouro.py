"""Sorteio da amostra-ouro e geração das planilhas de rotulagem:
``python -m validacao.amostra_ouro``.

- 60 repositórios sorteados da amostra final com ``random_state=42``;
- até 5 releases por repositório (na janela, sem pré-release, com comparação
  disponível), também com semente fixa;
- uma planilha em branco por avaliador, com links diretos e **sem** nenhuma
  informação da heurística.

Planilhas já existentes nunca são sobrescritas (use ``--forcar`` só antes de
qualquer rotulagem começar).
"""
import argparse
from pathlib import Path

import pandas as pd

from validacao.comum import AVALIADORES, PASTA_ROTULOS, arquivo_rotulos

SEMENTE = 42
N_REPOSITORIOS = 60
N_RELEASES = 5

COLUNAS_PLANILHA_REPOS = ["repositorio", "url_repositorio", "tipo_projeto", "entregas_reais", "observacoes"]
COLUNAS_PLANILHA_RELEASES = ["repositorio", "tag", "tag_anterior", "url_release", "url_compare",
                             "corretiva", "observacoes"]


def ler(caminho):
    return pd.read_csv(caminho, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def como_booleano(serie):
    return serie.str.strip().str.lower().isin(["true", "1", "sim"])


def sortear_repositorios(amostra_final, n=N_REPOSITORIOS, semente=SEMENTE):
    ordenada = amostra_final.sort_values("repositorio", key=lambda s: s.str.lower()).reset_index(drop=True)
    if len(ordenada) < n:
        raise ValueError(f"A amostra final tem {len(ordenada)} repositórios; são necessários {n}.")
    sorteados = ordenada.sample(n=n, random_state=semente)
    return sorteados.sort_values("repositorio", key=lambda s: s.str.lower()).reset_index(drop=True)


def releases_elegiveis(releases):
    filtro = (~como_booleano(releases["prerelease"])) & como_booleano(releases["comparacao_disponivel"])
    return releases[filtro]


def sortear_releases(releases, repositorios, n=N_RELEASES, semente=SEMENTE):
    candidatas = releases_elegiveis(releases)
    partes = []

    for repositorio in repositorios:
        do_repo = (candidatas[candidatas["repositorio"] == repositorio]
                   .sort_values(["published_at", "tag"]).reset_index(drop=True))
        if do_repo.empty:
            continue
        sorteadas = do_repo.sample(n=min(n, len(do_repo)), random_state=semente)
        partes.append(sorteadas.sort_values(["published_at", "tag"]))

    if not partes:
        return candidatas.iloc[0:0].copy()
    return pd.concat(partes, ignore_index=True)


def gerar_planilhas(repos, releases, pasta, avaliadores=AVALIADORES, forcar=False):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)

    planilha_repos = pd.DataFrame({
        "repositorio": repos["repositorio"],
        "url_repositorio": "https://github.com/" + repos["repositorio"],
        "tipo_projeto": "", "entregas_reais": "", "observacoes": "",
    })[COLUNAS_PLANILHA_REPOS]

    planilha_releases = releases.assign(corretiva="", observacoes="")[COLUNAS_PLANILHA_RELEASES]

    criados, preservados = [], []
    for avaliador in avaliadores:
        for nivel, tabela in (("repositorios", planilha_repos), ("releases", planilha_releases)):
            destino = arquivo_rotulos(pasta, avaliador, nivel)
            if destino.exists() and not forcar:
                preservados.append(destino)
                continue
            tabela.to_csv(destino, index=False, encoding="utf-8-sig", lineterminator="\n")
            criados.append(destino)

    return criados, preservados


def executar(resultados="resultados", validacao="validacao", forcar=False):
    resultados, validacao = Path(resultados), Path(validacao)
    amostra = ler(resultados / "amostra_final.csv")
    releases = ler(resultados / "releases_janela.csv")

    repos = sortear_repositorios(amostra)
    sorteadas = sortear_releases(releases, list(repos["repositorio"]))

    validacao.mkdir(parents=True, exist_ok=True)
    repos[["repositorio"]].to_csv(validacao / "amostra_ouro_repositorios.csv",
                                  index=False, encoding="utf-8-sig", lineterminator="\n")
    sorteadas[["repositorio", "tag", "tag_anterior", "published_at", "url_release", "url_compare"]].to_csv(
        validacao / "amostra_ouro_releases.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    criados, preservados = gerar_planilhas(repos, sorteadas, validacao / "rotulos", forcar=forcar)

    por_repo = sorteadas.groupby("repositorio").size()
    incompletos = int((por_repo < N_RELEASES).sum()) + (len(repos) - len(por_repo))
    print(f"Repositórios sorteados: {len(repos)} | releases sorteadas: {len(sorteadas)}")
    print(f"Repositórios com menos de {N_RELEASES} releases avaliáveis: {incompletos}")
    print(f"Planilhas criadas: {len(criados)} | preservadas (já existiam): {len(preservados)}")
    return repos, sorteadas


def main():
    parser = argparse.ArgumentParser(description="Sorteia a amostra-ouro e gera as planilhas")
    parser.add_argument("--resultados", default="resultados")
    parser.add_argument("--validacao", default="validacao")
    parser.add_argument("--forcar", action="store_true",
                        help="sobrescreve planilhas existentes (somente antes da rotulagem)")
    args = parser.parse_args()
    executar(args.resultados, args.validacao, args.forcar)


if __name__ == "__main__":
    main()
