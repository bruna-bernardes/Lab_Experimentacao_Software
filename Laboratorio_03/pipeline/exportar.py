"""Exportação offline dos dados coletados: ``python -m pipeline.exportar``.

Lê ``dados/janela_*/progresso`` e ``detalhes`` e gera, em ``resultados/``,
arquivos enxutos e versionáveis. Não usa token nem rede. Com eles, a
validação manual e a Sprint 3 rodam em qualquer máquina.

Arquivos gerados:
- ``amostra_final.csv``: repositórios elegíveis (a amostra congelada);
- ``funil_selecao.csv``: etapas do funil de seleção;
- ``releases_janela.csv``: uma linha por release publicada na janela
  (com pré-releases), com a release anterior mesmo que ela esteja fora;
- ``commits_releases.csv.gz``: commits incluídos em cada release;
- ``runs.csv.gz``: workflow runs válidas do default branch.
"""
import argparse
import json
import shutil
from pathlib import Path
from urllib.parse import quote

from pipeline.arquivos import escrever_csv
from pipeline.config import carregar_config, pasta_janela

COLUNAS_AMOSTRA = [
    "repositorio", "ordem_pool", "branch", "estrelas", "linguagem",
    "contribuidores", "idade_dias", "criado_em", "coletado_em"
]

COLUNAS_RELEASES = [
    "repositorio", "tag", "nome", "published_at", "prerelease",
    "tag_anterior", "published_at_anterior", "primeira_da_historia",
    "comparacao_disponivel", "n_commits", "tag_anterior_com_pre",
    "url_release", "url_compare"
]

COLUNAS_COMMITS = ["repositorio", "tag", "sha", "author_date", "mensagem_primeira_linha"]

COLUNAS_RUNS = [
    "repositorio", "workflow_id", "workflow_nome", "run_id", "conclusion",
    "created_at", "run_started_at", "updated_at"
]


def url_release(repositorio, tag):
    return f"https://github.com/{repositorio}/releases/tag/{quote(tag, safe='')}"


def url_compare(repositorio, base, head):
    if not base:
        return ""
    return f"https://github.com/{repositorio}/compare/{quote(base, safe='')}...{quote(head, safe='')}"


def dentro(data, inicio, fim):
    return bool(data) and inicio <= data <= fim


def linhas_releases(detalhes, inicio, fim):
    """Releases publicadas do repositório dentro da janela. ``tag_anterior`` segue a sequência
    principal (sem pré-releases), a mesma usada pelo lead time e pelo CFR (b);
    ``tag_anterior_com_pre`` segue a sequência com pré-releases (RQ 07)."""
    repositorio = detalhes["repositorio"]
    comparacoes = {c["tag"]: c for c in detalhes.get("comparacoes", [])}

    todas = detalhes.get("releases_todas")
    historico_completo = todas is not None
    if todas is None:  # detalhes da Sprint 1: só releases principais da janela
        todas = detalhes.get("releases", [])

    todas = sorted(
        (r for r in todas if not r.get("draft") and r.get("published_at")),
        key=lambda r: (r["published_at"], r["tag_name"])
    )

    linhas = []
    anterior_principal = None
    anterior_qualquer = None

    for release in todas:
        tag = release["tag_name"]
        pre = bool(release.get("prerelease"))
        comparacao = comparacoes.get(tag)

        if not pre and not historico_completo and comparacao:
            anterior_principal = {"tag_name": comparacao["tag_anterior"], "published_at": None}

        linha = {
            "repositorio": repositorio,
            "tag": tag,
            "nome": release.get("name") or "",
            "published_at": release["published_at"],
            "prerelease": pre,
            "tag_anterior_com_pre": anterior_qualquer["tag_name"] if anterior_qualquer else "",
            "url_release": url_release(repositorio, tag),
        }

        if not pre:
            tag_anterior = anterior_principal["tag_name"] if anterior_principal else ""
            linha.update({
                "tag_anterior": tag_anterior,
                "published_at_anterior": (anterior_principal or {}).get("published_at") or "",
                "primeira_da_historia": anterior_principal is None if historico_completo else "",
                "comparacao_disponivel": comparacao is not None,
                "n_commits": len(comparacao["commits"]) if comparacao else "",
                "url_compare": url_compare(repositorio, tag_anterior, tag),
            })
            anterior_principal = release

        if dentro(release["published_at"], inicio, fim):
            linhas.append(linha)
        anterior_qualquer = release

    return linhas


def primeira_linha(mensagem):
    return (mensagem or "").strip().splitlines()[0] if (mensagem or "").strip() else ""


def linhas_commits(detalhes):
    repositorio = detalhes["repositorio"]
    for comparacao in detalhes.get("comparacoes", []):
        for item in comparacao.get("commits", []):
            commit = item.get("commit", {})
            yield {
                "repositorio": repositorio,
                "tag": comparacao["tag"],
                "sha": item.get("sha", ""),
                "author_date": (commit.get("author") or {}).get("date", ""),
                "mensagem_primeira_linha": primeira_linha(commit.get("message")),
            }


def linhas_runs(detalhes):
    repositorio = detalhes["repositorio"]
    for run in detalhes.get("runs", []):
        yield {
            "repositorio": repositorio,
            "workflow_id": run.get("workflow_id"),
            "workflow_nome": run.get("name") or "",
            "run_id": run.get("id"),
            "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "run_started_at": run.get("run_started_at"),
            "updated_at": run.get("updated_at"),
        }


def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def exportar(config):
    pasta = pasta_janela(config)
    saida = Path(config.get("diretorio_resultados", "resultados"))
    saida.mkdir(parents=True, exist_ok=True)

    if not (pasta / "progresso").exists():
        raise FileNotFoundError(f"Nenhuma coleta encontrada em {pasta}. Rode antes: python -m pipeline")

    progresso = [carregar_json(a) for a in sorted((pasta / "progresso").glob("*.json"))]
    elegiveis = sorted(
        (r for r in progresso if r["status"] == "elegivel"),
        key=lambda r: r["repositorio"].lower()
    )

    amostra, releases, commits, runs = [], [], [], []
    for registro in elegiveis:
        nome = registro["repositorio"]
        arquivo = pasta / "detalhes" / f"{nome.replace('/', '__')}.json"
        if not arquivo.exists():
            raise FileNotFoundError(f"Detalhes ausentes para {nome}: {arquivo}")

        detalhes = carregar_json(arquivo)
        amostra.append({
            **registro["dados"],
            "ordem_pool": registro.get("ordem_pool"),
            "coletado_em": detalhes.get("coletado_em") or registro.get("processado_em", ""),
        })
        releases.extend(linhas_releases(detalhes, config["inicio"], config["fim"]))
        commits.extend(linhas_commits(detalhes))
        runs.extend(linhas_runs(detalhes))

    releases.sort(key=lambda r: (r["repositorio"].lower(), r["published_at"], r["tag"]))
    commits.sort(key=lambda c: (c["repositorio"].lower(), c["tag"], c["author_date"], c["sha"]))
    runs.sort(key=lambda r: (r["repositorio"].lower(), str(r["workflow_id"]), r["run_started_at"] or "", str(r["run_id"])))

    escrever_csv(saida / "amostra_final.csv", amostra, COLUNAS_AMOSTRA)
    escrever_csv(saida / "releases_janela.csv", releases, COLUNAS_RELEASES)
    escrever_csv(saida / "commits_releases.csv.gz", commits, COLUNAS_COMMITS)
    escrever_csv(saida / "runs.csv.gz", runs, COLUNAS_RUNS)

    if (pasta / "funil_selecao.csv").exists():
        shutil.copyfile(pasta / "funil_selecao.csv", saida / "funil_selecao.csv")

    resumo = {"repositorios": len(amostra), "releases": len(releases),
              "commits": len(commits), "runs": len(runs)}
    print(f"Exportação concluída em {saida}: {resumo}")
    return resumo


def main():
    parser = argparse.ArgumentParser(description="Exporta os dados coletados para CSVs versionáveis")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    exportar(carregar_config(args.config))


if __name__ == "__main__":
    main()
