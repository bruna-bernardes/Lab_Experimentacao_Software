"""Avaliação da heurística de release corretiva contra o consenso:
``python -m validacao.avaliar_heuristica --versao v1`` (ou ``--todas``).

Calcula precisão, recall e F1 com ``precision_recall_fscore_support`` do
scikit-learn (classe positiva = corretiva) e registra cada versão avaliada em
``validacao/heuristica_versoes.csv``. Os falsos positivos e negativos ficam em
``validacao/erros_heuristica_<versao>.csv`` para orientar o refinamento.
"""
import argparse
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from heuristica import DESCRICOES, VERSOES, eh_corretiva
from pipeline.arquivos import escrever_csv, ler_csv

LIMIAR_F1 = 0.70

COLUNAS_VERSOES = ["versao", "descricao_regra", "n_releases", "tp", "fp", "fn", "tn",
                   "precisao", "recall", "f1", "atinge_limiar", "data", "commit"]

COLUNAS_ERROS = ["repositorio", "tag", "tag_anterior", "consenso", "heuristica", "tipo_erro",
                 "url_compare", "mensagens"]


def commit_atual():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def metricas_binarias(y_real, y_previsto):
    """Precisão, recall, F1 e matriz de confusão, com 1 = corretiva."""
    precisao, recall, f1, _ = precision_recall_fscore_support(
        y_real, y_previsto, average="binary", pos_label=1, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_real, y_previsto, labels=[0, 1]).ravel()
    return {"precisao": float(precisao), "recall": float(recall), "f1": float(f1),
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}


def montar_casos(consenso, releases, commits):
    """Junta, para cada release do consenso, a tag anterior e as mensagens."""
    por_release = {(r["repositorio"], r["tag"]): r for r in releases}
    mensagens = defaultdict(list)
    for c in commits:
        mensagens[(c["repositorio"], c["tag"])].append(c["mensagem_primeira_linha"])

    casos, ausentes = [], []
    for linha in consenso:
        chave = (linha["repositorio"], linha["tag"])
        release = por_release.get(chave)
        if release is None:
            ausentes.append(chave)
            continue
        casos.append({
            "repositorio": chave[0], "tag": chave[1],
            "tag_anterior": release.get("tag_anterior", ""),
            "url_compare": release.get("url_compare", ""),
            "mensagens": mensagens.get(chave, []),
            "consenso": 1 if linha["corretiva"] == "sim" else 0,
        })

    if ausentes:
        raise ValueError(f"{len(ausentes)} releases do consenso não estão em releases_janela.csv: {ausentes[:3]}")
    return casos


def avaliar(casos, versao):
    previstos = [int(eh_corretiva(c["tag_anterior"], c["tag"], c["mensagens"], versao)) for c in casos]
    reais = [c["consenso"] for c in casos]
    resultado = metricas_binarias(reais, previstos)

    erros = []
    for caso, previsto in zip(casos, previstos):
        if previsto != caso["consenso"]:
            erros.append({**caso, "heuristica": previsto,
                          "tipo_erro": "falso_positivo" if previsto else "falso_negativo",
                          "mensagens": " | ".join(caso["mensagens"])[:2000]})
    return resultado, erros


def registrar_versao(caminho, linha):
    """Mantém uma linha por versão (reavaliar a mesma versão atualiza a linha)."""
    existentes = [l for l in ler_csv(caminho) if l["versao"] != linha["versao"]] if Path(caminho).exists() else []
    escrever_csv(caminho, sorted(existentes + [linha], key=lambda l: l["versao"]), COLUNAS_VERSOES)


def executar(versoes, validacao="validacao", resultados="resultados"):
    validacao, resultados = Path(validacao), Path(resultados)
    casos = montar_casos(
        ler_csv(validacao / "consenso_releases.csv"),
        ler_csv(resultados / "releases_janela.csv"),
        ler_csv(resultados / "commits_releases.csv.gz"),
    )

    linhas = []
    for versao in versoes:
        resultado, erros = avaliar(casos, versao)
        linha = {
            "versao": versao, "descricao_regra": DESCRICOES.get(versao, ""),
            "n_releases": len(casos), **resultado,
            "precisao": round(resultado["precisao"], 4), "recall": round(resultado["recall"], 4),
            "f1": round(resultado["f1"], 4), "atinge_limiar": resultado["f1"] >= LIMIAR_F1,
            "data": date.today().isoformat(), "commit": commit_atual(),
        }
        registrar_versao(validacao / "heuristica_versoes.csv", linha)
        escrever_csv(validacao / f"erros_heuristica_{versao}.csv", erros, COLUNAS_ERROS)
        linhas.append(linha)
        print(f"{versao}: P = {linha['precisao']:.3f} R = {linha['recall']:.3f} F1 = {linha['f1']:.3f} "
              f"(TP {linha['tp']}, FP {linha['fp']}, FN {linha['fn']}, TN {linha['tn']}) "
              f"{'≥' if linha['atinge_limiar'] else '<'} {LIMIAR_F1}")
    return linhas


def main():
    parser = argparse.ArgumentParser(description="Avalia a heurística de release corretiva")
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--versao", choices=sorted(VERSOES))
    grupo.add_argument("--todas", action="store_true")
    parser.add_argument("--validacao", default="validacao")
    parser.add_argument("--resultados", default="resultados")
    args = parser.parse_args()

    versoes = sorted(VERSOES) if args.todas else [args.versao]
    executar(versoes, args.validacao, args.resultados)


if __name__ == "__main__":
    main()
