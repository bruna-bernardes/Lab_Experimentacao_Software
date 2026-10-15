"""Pipeline de coleta: ``python -m pipeline --config config.json``.

Fluxo por candidato (Sprint 2): Actions → metadados básicos (1 chamada) →
releases → workflow runs → contribuidores (apenas elegíveis) → commits entre
releases. Cada repositório processado gera um arquivo em ``progresso/``, o que
permite retomar a coleta exatamente de onde parou.
"""
import argparse
import csv
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pipeline.api import GitHubAPI
from pipeline.config import carregar_config, pasta_janela
from pipeline.releases import coletar_dados_releases, coletar_tags, converter_data
from pipeline.selecao import (
    contar_contribuidores, info_repositorio, montar_pool, ordenar_pool, possui_actions
)
from pipeline.workflows import coletar_runs
from metricas import (
    calcular_cfr_ci, calcular_recuperacao, lead_time_por_commit, lead_time_por_release
)

COLUNAS = [
    "repositorio", "branch", "estrelas", "linguagem",
    "contribuidores", "idade_dias", "releases", "runs_validas",
    "lead_time_release_horas", "lead_time_commit_horas",
    "cfr_ci", "recuperacao_horas", "episodios_censurados",
    "comparacoes_ignoradas", "proporcao_censura"
]

COLUNAS_SELECIONADOS = ["ordem_pool"] + COLUNAS

CONCLUSOES_VALIDAS = {"success", "failure", "timed_out", "startup_failure"}

STATUS_FINAIS = {
    "sem_actions", "releases_insuficientes", "runs_insuficientes",
    "erro_persistente", "elegivel"
}

ETAPAS_FUNIL = [
    "populacao_busca", "candidatos_examinados", "sem_actions", "com_actions",
    "releases_insuficientes", "runs_insuficientes", "elegiveis",
    "erros_persistentes", "erros_pendentes", "amostra_final"
]

CAMPOS_RELEASE = ["tag_name", "name", "draft", "prerelease", "published_at", "created_at", "html_url"]


def agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def nome_arquivo(repositorio):
    return f"{repositorio.replace('/', '__')}.json"


def salvar_json(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")

    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    os.replace(temporario, caminho)


def salvar_csv(caminho, dados, colunas):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    temporario = caminho.with_name(f"{caminho.stem}_{uuid.uuid4().hex}.tmp")

    try:
        with open(temporario, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=colunas, extrasaction="ignore")
            escritor.writeheader()
            escritor.writerows(dados)

        for tentativa in range(5):
            try:
                os.replace(temporario, caminho)
                return
            except PermissionError:
                if tentativa == 4:
                    raise
                print(f"Arquivo bloqueado: {caminho.name}. Tentando novamente...")
                time.sleep(2 ** tentativa)
    finally:
        if temporario.exists():
            temporario.unlink()


def carregar_progresso(pasta):
    progresso = {}

    for arquivo in (Path(pasta) / "progresso").glob("*.json"):
        with open(arquivo, "r", encoding="utf-8") as f:
            registro = json.load(f)
            progresso[registro["repositorio"]] = registro

    return progresso


def calcular_funil(progresso, populacao=None):
    funil = {etapa: 0 for etapa in ETAPAS_FUNIL}
    funil["populacao_busca"] = populacao if populacao is not None else len(progresso)

    for registro in progresso.values():
        status = registro["status"]
        funil["candidatos_examinados"] += 1

        if status == "sem_actions":
            funil["sem_actions"] += 1
        elif status in ("releases_insuficientes", "runs_insuficientes"):
            funil["com_actions"] += 1
            funil[status] += 1
        elif status == "elegivel":
            funil["com_actions"] += 1
            funil["elegiveis"] += 1
        elif status == "erro_persistente":
            funil["erros_persistentes"] += 1
        else:
            funil["erros_pendentes"] += 1

    funil["amostra_final"] = funil["elegiveis"]
    return funil


def atualizar_resultados(pasta, progresso, populacao=None):
    selecionados = sorted(
        (r["dados"] | {"ordem_pool": r.get("ordem_pool")}
         for r in progresso.values() if r["status"] == "elegivel"),
        key=lambda d: (d.get("ordem_pool") or 0, d["repositorio"])
    )
    funil = calcular_funil(progresso, populacao)

    salvar_csv(pasta / "repositorios_selecionados.csv", selecionados, COLUNAS_SELECIONADOS)
    salvar_csv(
        pasta / "funil_selecao.csv",
        [{"etapa": etapa, "quantidade": valor} for etapa, valor in funil.items()],
        ["etapa", "quantidade"]
    )

    return funil


def obter_pool(api, pasta, config):
    """O pool é salvo em disco na primeira execução e reutilizado depois, para
    que a ordem dos candidatos não mude mesmo que o cache HTTP seja apagado."""
    arquivo = pasta / "pool_candidatos.json"

    if arquivo.exists():
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Montando o pool de candidatos (todas as faixas de estrelas)...")
    pool = ordenar_pool(montar_pool(api), config["semente_amostragem"])
    registro = {
        "data_busca": agora(),
        "semente": config["semente_amostragem"],
        "total": len(pool),
        "candidatos": pool
    }
    salvar_json(arquivo, registro)
    return registro


def resumir_release(release):
    return {campo: release.get(campo) for campo in CAMPOS_RELEASE}


def releases_publicadas(todas):
    """Releases publicadas (sem drafts), incluindo pré-releases, em ordem."""
    publicadas = [r for r in todas if not r.get("draft") and r.get("published_at")]
    return sorted(publicadas, key=lambda r: r["published_at"])


def releases_principais_na_janela(publicadas, inicio, fim):
    inicio, fim = converter_data(inicio), converter_data(fim)
    return [
        r for r in publicadas
        if not r.get("prerelease") and inicio <= converter_data(r["published_at"]) <= fim
    ]


def processar_repositorio(api, nome, config):
    """Processa um candidato e devolve o registro de progresso e, para os
    elegíveis, os detalhes a salvar. Os filtros estão em ordem de custo."""
    inicio, fim = config["inicio"], config["fim"]

    if not possui_actions(api, {"full_name": nome}):
        return {"repositorio": nome, "status": "sem_actions"}, None

    dados = info_repositorio(api, nome, fim)

    todas = api.paginas(f"/repos/{nome}/releases")
    publicadas = releases_publicadas(todas)
    releases = releases_principais_na_janela(publicadas, inicio, fim)

    if len(releases) < 5:
        return {"repositorio": nome, "status": "releases_insuficientes",
                "releases": len(releases)}, None

    runs = coletar_runs(api, nome, dados["branch"], inicio, fim)
    runs_validas = [r for r in runs if r.get("conclusion") in CONCLUSOES_VALIDAS]

    if len(runs_validas) < 50:
        return {"repositorio": nome, "status": "runs_insuficientes",
                "releases": len(releases), "runs_validas": len(runs_validas)}, None

    dados["contribuidores"] = contar_contribuidores(api, nome)
    comparacoes, ignoradas = coletar_dados_releases(api, nome, inicio, fim)
    recuperacao = calcular_recuperacao(runs_validas)

    dados.update({
        "releases": len(releases),
        "runs_validas": len(runs_validas),
        "lead_time_release_horas": lead_time_por_release(comparacoes),
        "lead_time_commit_horas": lead_time_por_commit(comparacoes),
        "cfr_ci": calcular_cfr_ci(runs_validas),
        "recuperacao_horas": recuperacao["mediana_horas"],
        "episodios_censurados": recuperacao["episodios_censurados"],
        "comparacoes_ignoradas": ignoradas,
        "proporcao_censura": recuperacao["proporcao_censura"]
    })

    detalhes = {
        "repositorio": nome,
        "coletado_em": agora(),
        "branch": dados["branch"],
        "releases": releases,
        "releases_todas": [resumir_release(r) for r in publicadas],
        "comparacoes": comparacoes,
        "runs": runs_validas,
    }

    if config.get("coletar_tags", True):
        detalhes["tags"] = [
            {"name": t.get("name"), "sha": (t.get("commit") or {}).get("sha")}
            for t in coletar_tags(api, nome)
        ]

    return {"repositorio": nome, "status": "elegivel", "dados": dados}, detalhes


def registrar_erro(pasta, registro_anterior, nome, erro, max_tentativas):
    tentativas = (registro_anterior or {}).get("tentativas", 0) + 1
    status = "erro_persistente" if tentativas >= max_tentativas else "erro"

    arquivo_erros = pasta / "erros_coleta.json"
    erros = []
    if arquivo_erros.exists():
        with open(arquivo_erros, "r", encoding="utf-8") as f:
            erros = json.load(f)

    erros.append({"repositorio": nome, "erro": str(erro), "data": agora(), "tentativa": tentativas})
    salvar_json(arquivo_erros, erros)

    return {"repositorio": nome, "status": status, "tentativas": tentativas, "ultimo_erro": str(erro)}


def executar(config, api=None):
    api = api or GitHubAPI(cache_dir=config.get("cache_dir", ".cache/github"))
    quantidade = config.get("quantidade", 300)
    maximo = config.get("maximo_candidatos", 6000)
    max_tentativas = config.get("max_tentativas_erro", 3)

    if quantidade < 1 or maximo < 1:
        raise ValueError("Quantidade e máximo de candidatos devem ser positivos.")

    pasta = pasta_janela(config)
    pasta.mkdir(parents=True, exist_ok=True)

    pool = obter_pool(api, pasta, config)
    populacao = pool["total"]
    progresso = carregar_progresso(pasta)
    funil = atualizar_resultados(pasta, progresso, populacao)

    print(f"\nPopulação da busca: {populacao}")
    print(f"Repositórios já processados: {funil['candidatos_examinados']}")
    print(f"Elegíveis recuperados: {funil['elegiveis']}")

    for candidato in pool["candidatos"][:maximo]:
        if funil["elegiveis"] >= quantidade:
            break

        nome = candidato["repositorio"]
        anterior = progresso.get(nome)

        if anterior and anterior["status"] in STATUS_FINAIS:
            continue

        print(f"\n[{candidato['ordem_pool']}] Analisando: {nome}")

        try:
            registro, detalhes = processar_repositorio(api, nome, config)

            if detalhes is not None:
                salvar_json(pasta / "detalhes" / nome_arquivo(nome), detalhes)

            print(f"Status: {registro['status']}")

        except Exception as erro:
            print(f"Erro em {nome}: {erro}")
            registro = registrar_erro(pasta, anterior, nome, erro, max_tentativas)

        registro["ordem_pool"] = candidato["ordem_pool"]
        registro["processado_em"] = agora()
        salvar_json(pasta / "progresso" / nome_arquivo(nome), registro)

        progresso[nome] = registro
        funil = atualizar_resultados(pasta, progresso, populacao)
        print(f"Progresso salvo: {funil['elegiveis']}/{quantidade} elegíveis")

    print("\nFUNIL")
    for etapa, valor in funil.items():
        print(f"{etapa}: {valor}")

    if funil["elegiveis"] >= quantidade:
        print("\nQuantidade solicitada atingida.")
    print(f"Arquivos salvos em: {pasta}")
    print("Próximo passo: python -m pipeline.exportar --config <config>")
    return funil


def main():
    parser = argparse.ArgumentParser(description="Coleta de métricas DORA")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()

    executar(carregar_config(args.config))


if __name__ == "__main__":
    main()
