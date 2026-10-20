
import argparse
import csv
import gzip
import json
import os
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import quote

import ijson

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
    """Mantém a interface original, aceitando metadados compactos de comparações."""
    repositorio = detalhes["repositorio"]
    comparacoes = {c["tag"]: c for c in detalhes.get("comparacoes", [])}
    todas = detalhes.get("releases_todas")
    historico_completo = todas is not None
    if todas is None:
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
            anterior_principal = {"tag_name": comparacao.get("tag_anterior", ""), "published_at": None}
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
                "n_commits": (comparacao.get("n_commits", len(comparacao.get("commits", [])))
                              if comparacao else ""),
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
            commit = item.get("commit") or {}
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
    """Compatibilidade com os testes e JSONs pequenos; não usar nos detalhes grandes."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def ler_itens(caminho, prefixo):
    with open(caminho, "rb") as arquivo:
        yield from ijson.items(arquivo, prefixo)


def ler_campo(caminho, prefixo, padrao=None):
    with open(caminho, "rb") as arquivo:
        return next(ijson.items(arquivo, prefixo), padrao)


def _comparacoes_compactas(caminho):
    """Lê tags e conta commits sem materializar o array de commits em RAM."""
    comparacoes = []
    atual = None
    with open(caminho, "rb") as arquivo:
        for prefixo, evento, valor in ijson.parse(arquivo):
            if prefixo == "comparacoes.item" and evento == "start_map":
                atual = {"tag": "", "tag_anterior": "", "n_commits": 0}
            elif atual is not None and prefixo in ("comparacoes.item.tag", "comparacoes.item.tag_anterior"):
                if evento in ("string", "null"):
                    atual[prefixo.rsplit(".", 1)[-1]] = valor or ""
            elif atual is not None and prefixo == "comparacoes.item.commits.item" and evento == "start_map":
                atual["n_commits"] += 1
            elif prefixo == "comparacoes.item" and evento == "end_map":
                comparacoes.append(atual)
                atual = None
    return comparacoes


def _commits_stream(caminho, repositorio):
    """Itera sobre cada commit de comparação, construindo somente um commit por vez."""
    tag = ""
    construtor = None
    with open(caminho, "rb") as arquivo:
        for prefixo, evento, valor in ijson.parse(arquivo):
            if prefixo == "comparacoes.item.tag" and evento == "string":
                tag = valor
            elif prefixo == "comparacoes.item.commits.item" and evento == "start_map":
                construtor = ijson.common.ObjectBuilder()
                construtor.event(evento, valor)
            elif construtor is not None:
                construtor.event(evento, valor)
                if prefixo == "comparacoes.item.commits.item" and evento == "end_map":
                    item = construtor.value
                    commit = item.get("commit") or {}
                    yield {
                        "repositorio": repositorio,
                        "tag": tag,
                        "sha": item.get("sha", ""),
                        "author_date": (commit.get("author") or {}).get("date", ""),
                        "mensagem_primeira_linha": primeira_linha(commit.get("message")),
                    }
                    construtor = None


def _runs_stream(caminho, repositorio):
    for run in ler_itens(caminho, "runs.item"):
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


class _CsvIncremental:
    """Grava em arquivos temporários, sem acumular linhas; publica ao concluir."""
    def __init__(self, caminho, colunas):
        self.caminho = Path(caminho)
        self.tmp = Path(str(caminho) + ".tmp")
        self.colunas = colunas
        self.arquivo = None
        self.escritor = None
        self.total = 0

    def __enter__(self):
        self.tmp.parent.mkdir(parents=True, exist_ok=True)
        if str(self.caminho).endswith(".gz"):
            self.arquivo = gzip.open(self.tmp, "wt", encoding="utf-8-sig", newline="")
        else:
            self.arquivo = open(self.tmp, "w", encoding="utf-8-sig", newline="")
        self.escritor = csv.DictWriter(self.arquivo, fieldnames=self.colunas, extrasaction="ignore")
        self.escritor.writeheader()
        return self

    def adicionar(self, linhas):
        for linha in linhas:
            self.escritor.writerow(linha)
            self.total += 1

    def __exit__(self, tipo, valor, traceback):
        self.arquivo.close()
        if tipo is None:
            os.replace(self.tmp, self.caminho)
        return False


def exportar(config):
    pasta = pasta_janela(config)
    saida = Path(config.get("diretorio_resultados", "resultados"))
    saida.mkdir(parents=True, exist_ok=True)

    if not (pasta / "progresso").exists():
        raise FileNotFoundError(f"Nenhuma coleta encontrada em {pasta}. Rode antes: python -m pipeline")

    progresso = [carregar_json(a) for a in sorted((pasta / "progresso").glob("*.json"))]
    elegiveis = sorted((r for r in progresso if r["status"] == "elegivel"),
                      key=lambda r: r["repositorio"].lower())
    print(f"Repositórios elegíveis registrados: {len(elegiveis)}", flush=True)

    with (_CsvIncremental(saida / "amostra_final.csv", COLUNAS_AMOSTRA) as amostra,
          _CsvIncremental(saida / "releases_janela.csv", COLUNAS_RELEASES) as releases,
          _CsvIncremental(saida / "commits_releases.csv.gz", COLUNAS_COMMITS) as commits,
          _CsvIncremental(saida / "runs.csv.gz", COLUNAS_RUNS) as runs):
        for numero, registro in enumerate(elegiveis, 1):
            nome = registro["repositorio"]
            arquivo = pasta / "detalhes" / f"{nome.replace('/', '__')}.json"
            if not arquivo.exists():
                raise FileNotFoundError(f"Detalhes ausentes para {nome}: {arquivo}")

            coletado_em = ler_campo(arquivo, "coletado_em", "")
            amostra.adicionar([{**registro["dados"], "ordem_pool": registro.get("ordem_pool"),
                                "coletado_em": coletado_em or registro.get("processado_em", "")}])

            historico = ler_campo(arquivo, "releases_todas", None)
            # releases_todas tende a ser pequeno, mas a leitura abaixo isola este campo.
            if historico is None:
                historico = ler_campo(arquivo, "releases", [])
                detalhes = {"repositorio": nome, "releases": historico}
            else:
                detalhes = {"repositorio": nome, "releases_todas": historico}
            detalhes["comparacoes"] = _comparacoes_compactas(arquivo)
            releases.adicionar(linhas_releases(detalhes, config["inicio"], config["fim"]))
            commits.adicionar(_commits_stream(arquivo, nome))
            runs.adicionar(_runs_stream(arquivo, nome))
            print(f"Exportados {numero}/{len(elegiveis)}: {nome}", flush=True)

        resumo = {"repositorios": amostra.total, "releases": releases.total,
                  "commits": commits.total, "runs": runs.total}

    funil = pasta / "funil_selecao.csv"
    if funil.exists():
        shutil.copyfile(funil, saida / "funil_selecao.csv")
    print(f"Exportação concluída em {saida}: {resumo}")
    return resumo


def main():
    parser = argparse.ArgumentParser(description="Exporta dados coletados para CSVs versionáveis")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    exportar(carregar_config(args.config))


if __name__ == "__main__":
    main()
