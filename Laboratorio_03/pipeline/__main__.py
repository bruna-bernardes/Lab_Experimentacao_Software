
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

from pipeline.api import GitHubAPI
from pipeline.selecao import candidatos, metadados, possui_actions
from pipeline.releases import coletar_releases, coletar_dados_releases
from pipeline.workflows import coletar_runs
from metricas import lead_time_por_release, lead_time_por_commit, calcular_cfr_ci, calcular_recuperacao
import time
import uuid

COLUNAS = [
    "repositorio", "branch", "estrelas", "linguagem",
    "contribuidores", "idade_dias", "releases", "runs_validas",
    "lead_time_release_horas", "lead_time_commit_horas",
    "cfr_ci", "recuperacao_horas", "episodios_censurados",
    "comparacoes_ignoradas", "proporcao_censura"
]

CONCLUSOES_VALIDAS = {"success", "failure", "timed_out", "startup_failure"}


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
            escritor = csv.DictWriter(arquivo, fieldnames=colunas)
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

    for arquivo in (pasta / "progresso").glob("*.json"):
        with open(arquivo, "r", encoding="utf-8") as f:
            registro = json.load(f)
            progresso[registro["repositorio"]] = registro

    return progresso


def atualizar_resultados(pasta, progresso):
    selecionados = [
        registro["dados"] for registro in progresso.values()
        if registro["status"] == "elegivel"
    ]

    funil = {
        "candidatos": len(progresso),
        "sem_actions": 0,
        "com_actions": 0,
        "releases_insuficientes": 0,
        "runs_insuficientes": 0,
        "elegiveis": len(selecionados)
    }

    for registro in progresso.values():
        status = registro["status"]

        if status == "sem_actions":
            funil["sem_actions"] += 1
        else:
            funil["com_actions"] += 1

        if status in ("releases_insuficientes", "runs_insuficientes"):
            funil[status] += 1

    salvar_csv(
        pasta / "repositorios_selecionados.csv",
        selecionados, COLUNAS
    )

    salvar_csv(
        pasta / "funil_selecao.csv",
        [{"etapa": etapa, "quantidade": valor} for etapa, valor in funil.items()],
        ["etapa", "quantidade"]
    )

    return funil


def executar(config):
    api = GitHubAPI()
    inicio, fim = config["inicio"], config["fim"]
    quantidade = config.get("quantidade", 2)
    maximo = config.get("maximo_candidatos", 100)

    if quantidade < 1 or maximo < 1:
        raise ValueError("Quantidade e máximo de candidatos devem ser positivos.")

    chave = hashlib.sha256(
        json.dumps([inicio, fim, "selecao_v1"]).encode()
    ).hexdigest()[:12]

    pasta = Path(config.get("diretorio_saida", "dados")) / f"janela_{chave}"
    pasta.mkdir(parents=True, exist_ok=True)

    progresso = carregar_progresso(pasta)
    erros = []

    funil = atualizar_resultados(pasta, progresso)
    print(f"\nRepositórios já processados: {funil['candidatos']}")
    print(f"Elegíveis recuperados: {funil['elegiveis']}")

    if funil["elegiveis"] >= quantidade:
        print("\nQuantidade solicitada já atingida.")
        print(f"Resultados disponíveis em: {pasta}")
        return

    for repo in candidatos(api, maximo=maximo):
        nome = repo["full_name"]

        if nome in progresso:
            continue

        if len(progresso) >= maximo or funil["elegiveis"] >= quantidade:
            break

        print(f"\nAnalisando: {nome}")

        try:
            if not possui_actions(api, repo):
                registro = {"repositorio": nome, "status": "sem_actions"}
                print("Descartado: sem GitHub Actions")

            else:
                dados = metadados(api, repo)
                releases = coletar_releases(api, nome, inicio, fim)

                if len(releases) < 5:
                    registro = {
                        "repositorio": nome,
                        "status": "releases_insuficientes"
                    }
                    print(f"Descartado: {len(releases)} releases")

                else:
                    runs = coletar_runs(api, nome, dados["branch"], inicio, fim)
                    runs_validas = [
                        r for r in runs
                        if r.get("conclusion") in CONCLUSOES_VALIDAS
                    ]

                    if len(runs_validas) < 50:
                        registro = {
                            "repositorio": nome,
                            "status": "runs_insuficientes"
                        }
                        print(f"Descartado: {len(runs_validas)} runs validas")

                    else:
                        comparacoes, ignoradas = coletar_dados_releases(
                            api, nome, inicio, fim
                        )
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
                            "releases": releases,
                            "comparacoes": comparacoes,
                            "runs": runs_validas
                        }

                        salvar_json(
                            pasta / "detalhes" / f"{nome.replace('/', '__')}.json",
                            detalhes
                        )

                        registro = {
                            "repositorio": nome,
                            "status": "elegivel",
                            "dados": dados
                        }
                        print(f"Selecionado: {nome}")

            salvar_json(
                pasta / "progresso" / f"{nome.replace('/', '__')}.json",
                registro
            )

            progresso[nome] = registro
            funil = atualizar_resultados(pasta, progresso)
            print(f"Progresso salvo: {funil['elegiveis']}/{quantidade} elegiveis")

        except Exception as erro:
            print(f"Erro em {nome}: {erro}")
            erros.append({"repositorio": nome, "erro": str(erro)})
            salvar_json(pasta / "erros_coleta.json", erros)

    print("\nFUNIL FINAL")
    for etapa, valor in funil.items():
        print(f"{etapa}: {valor}")

    print(f"\nRepositorios elegiveis: {funil['elegiveis']}/{quantidade}")
    print(f"Erros nesta execucao: {len(erros)}")
    print(f"Arquivos salvos em: {pasta}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

    executar(config)


if __name__ == "__main__":
    main()
