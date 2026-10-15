"""Recálculo offline das métricas e geração do dataset final:
``python -m pipeline.consolidar --config config.json``.

Lê os arquivos exportados por ``pipeline.exportar`` (sem token e sem rede),
recalcula todas as métricas DORA nas variantes obrigatórias e grava
``resultados/dataset_final.csv``. Como não depende da API, pode ser
reexecutado sempre que uma definição mudar, por exemplo uma nova versão da
heurística de release corretiva (campo ``versao_heuristica`` do config).
"""
import argparse
from collections import defaultdict
from pathlib import Path

from heuristica import eh_corretiva
from metricas import (
    calcular_cfr_ci, calcular_cfr_entrega, calcular_recuperacao, data_hora,
    deployment_frequency, lead_time_por_commit, lead_time_por_release
)
from pipeline.arquivos import booleano, escrever_csv, ler_csv, numero
from pipeline.config import carregar_config

FALHAS = {"failure", "timed_out", "startup_failure"}

COLUNAS_DATASET = [
    # metadados
    "repositorio", "branch", "estrelas", "linguagem", "contribuidores", "idade_dias",
    # RQ 01
    "releases_janela", "deployment_frequency_semana",
    # RQ 02
    "lead_time_release_horas", "lead_time_commit_horas", "releases_lead_time",
    "releases_ignoradas_primeira", "releases_ignoradas_comparacao",
    "releases_sem_commits", "commits_lead_time_negativo",
    # RQ 03 (a)
    "runs_sucesso", "runs_falha", "cfr_ci",
    # RQ 03 (b)
    "releases_avaliadas_cfr_entrega", "releases_falhas_cfr_entrega",
    "releases_censuradas_cfr_entrega", "cfr_entrega", "versao_heuristica",
    # RQ 04
    "recuperacao_horas", "episodios_recuperados", "episodios_censurados", "proporcao_censura",
    # validação manual
    "amostra_ouro", "tipo_projeto_consenso", "entregas_reais_consenso",
]


def agrupar(linhas, chave="repositorio"):
    grupos = defaultdict(list)
    for linha in linhas:
        grupos[linha[chave]].append(linha)
    return grupos


def metricas_lead_time(releases_principais, commits_por_tag):
    estrutura = []
    ignoradas_primeira = ignoradas_comparacao = sem_commits = negativos = 0
    com_valor = 0

    for release in releases_principais:
        if booleano(release.get("primeira_da_historia")):
            ignoradas_primeira += 1
            continue

        if not booleano(release.get("comparacao_disponivel")):
            ignoradas_comparacao += 1
            continue

        commits = commits_por_tag.get(release["tag"], [])
        if not commits:
            sem_commits += 1
            continue

        publicada = data_hora(release["published_at"])
        datas = [c["author_date"] for c in commits if c.get("author_date")]
        negativos += sum(publicada < data_hora(d) for d in datas)

        if datas and publicada >= min(data_hora(d) for d in datas):
            com_valor += 1

        estrutura.append({
            "published_at": release["published_at"],
            "commits": [{"commit": {"author": {"date": d}}} for d in datas],
        })

    return {
        "lead_time_release_horas": lead_time_por_release(estrutura),
        "lead_time_commit_horas": lead_time_por_commit(estrutura),
        "releases_lead_time": com_valor,
        "releases_ignoradas_primeira": ignoradas_primeira,
        "releases_ignoradas_comparacao": ignoradas_comparacao,
        "releases_sem_commits": sem_commits,
        "commits_lead_time_negativo": negativos,
    }


def metricas_cfr_entrega(releases_principais, commits_por_tag, inicio, fim, versao):
    def classificar(anterior, atual):
        mensagens = [c["mensagem_primeira_linha"] for c in commits_por_tag.get(atual["tag"], [])]
        return eh_corretiva(atual.get("tag_anterior"), atual["tag"], mensagens, versao)

    resultado = calcular_cfr_entrega(releases_principais, classificar, inicio, fim)
    return {
        "releases_avaliadas_cfr_entrega": resultado["avaliadas"],
        "releases_falhas_cfr_entrega": resultado["falhas"],
        "releases_censuradas_cfr_entrega": resultado["censuradas"],
        "cfr_entrega": resultado["cfr"],
        "versao_heuristica": versao,
    }


def metricas_ci(runs):
    runs = [
        {**r, "workflow_id": r["workflow_id"]}
        for r in runs if r.get("conclusion")
    ]
    recuperacao = calcular_recuperacao(runs)

    return {
        "runs_sucesso": sum(r["conclusion"] == "success" for r in runs),
        "runs_falha": sum(r["conclusion"] in FALHAS for r in runs),
        "cfr_ci": calcular_cfr_ci(runs),
        "recuperacao_horas": recuperacao["mediana_horas"],
        "episodios_recuperados": recuperacao["episodios_recuperados"],
        "episodios_censurados": recuperacao["episodios_censurados"],
        "proporcao_censura": recuperacao["proporcao_censura"],
    }


def carregar_consenso(caminho):
    if not Path(caminho).exists():
        return {}
    return {linha["repositorio"]: linha for linha in ler_csv(caminho)}


def consolidar_repositorio(repo, releases, commits, runs, config, consenso=None):
    inicio, fim = config["inicio"], config["fim"]
    versao = config.get("versao_heuristica", "v1")

    principais = sorted(
        (r for r in releases if not booleano(r.get("prerelease"))),
        key=lambda r: (r["published_at"], r["tag"])
    )
    commits_por_tag = agrupar(commits, "tag")

    linha = {campo: repo.get(campo) for campo in
             ("repositorio", "branch", "estrelas", "linguagem", "contribuidores", "idade_dias")}
    linha["releases_janela"] = len(principais)
    linha["deployment_frequency_semana"] = deployment_frequency(len(principais), inicio, fim)
    linha.update(metricas_lead_time(principais, commits_por_tag))
    linha.update(metricas_cfr_entrega(principais, commits_por_tag, inicio, fim, versao))
    linha.update(metricas_ci(runs))

    rotulo = (consenso or {}).get(repo["repositorio"])
    linha["amostra_ouro"] = rotulo is not None
    linha["tipo_projeto_consenso"] = (rotulo or {}).get("tipo_projeto", "")
    linha["entregas_reais_consenso"] = (rotulo or {}).get("entregas_reais", "")
    return linha


def consolidar(config):
    resultados = Path(config.get("diretorio_resultados", "resultados"))
    validacao = Path(config.get("diretorio_validacao", "validacao"))

    amostra = ler_csv(resultados / "amostra_final.csv")
    releases = agrupar(ler_csv(resultados / "releases_janela.csv"))
    commits = agrupar(ler_csv(resultados / "commits_releases.csv.gz"))
    runs = agrupar(ler_csv(resultados / "runs.csv.gz"))
    consenso = carregar_consenso(validacao / "consenso_repositorios.csv")

    dataset = [
        consolidar_repositorio(
            repo, releases.get(repo["repositorio"], []), commits.get(repo["repositorio"], []),
            runs.get(repo["repositorio"], []), config, consenso
        )
        for repo in sorted(amostra, key=lambda r: r["repositorio"].lower())
    ]

    for linha in dataset:
        for campo in ("estrelas", "contribuidores", "idade_dias"):
            linha[campo] = numero(linha[campo])

    escrever_csv(resultados / "dataset_final.csv", dataset, COLUNAS_DATASET)
    print(f"dataset_final.csv: {len(dataset)} repositórios "
          f"(heurística {config.get('versao_heuristica', 'v1')}, "
          f"{sum(l['amostra_ouro'] for l in dataset)} na amostra-ouro com consenso)")
    return dataset


def main():
    parser = argparse.ArgumentParser(description="Recalcula as métricas e gera o dataset final")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    consolidar(carregar_config(args.config))


if __name__ == "__main__":
    main()
