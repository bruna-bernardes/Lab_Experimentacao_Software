import csv
import json
import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(
    LAB_DIR,
    "data"
)

DATA_EXTRAS_DIR = os.path.join(
    LAB_DIR,
    "data_extras"
)

os.makedirs(
    DATA_EXTRAS_DIR,
    exist_ok=True
)

REPOS_CSV = os.path.join(
    DATA_DIR,
    "repositorios_1000.csv"
)

GRAFICO_RQ01 = os.path.join(
    DATA_EXTRAS_DIR,
    "rq01_distribuicao_idade.png"
)

GRAFICO_RQ02 = os.path.join(
    DATA_EXTRAS_DIR,
    "rq02_distribuicao_pull_requests.png"
)

SUMMARY_JSON = os.path.join(
    DATA_EXTRAS_DIR,
    "rq01_rq02_summary.json"
)


def carregar_dados():
    if not os.path.exists(REPOS_CSV):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {REPOS_CSV}"
        )

    dados = []
    ignorados = 0

    agora = datetime.now(timezone.utc)

    with open(
        REPOS_CSV,
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        for row in csv.DictReader(arquivo):
            try:
                created_at = row.get(
                    "created_at",
                    ""
                ).strip()

                if not created_at:
                    ignorados += 1
                    continue

                data_criacao = datetime.fromisoformat(
                    created_at.replace(
                        "Z",
                        "+00:00"
                    )
                )

                idade_anos = (
                    agora - data_criacao
                ).days / 365.25

                merged_prs = int(
                    row["merged_pull_requests"]
                )

                dados.append({
                    "repository":
                        row["repository"],

                    "age_years":
                        idade_anos,

                    "merged_pull_requests":
                        merged_prs
                })

            except (
                KeyError,
                ValueError,
                TypeError
            ):
                ignorados += 1

    print(
        f"{len(dados)} repositórios válidos carregados."
    )

    if ignorados:
        print(
            f"{ignorados} registro(s) ignorado(s)."
        )

    return dados


def gerar_grafico_rq01(dados):
    faixas = {
        "0–2 anos": 0,
        "3–5 anos": 0,
        "6–8 anos": 0,
        "9–11 anos": 0,
        "12–15 anos": 0,
        "Mais de 15 anos": 0
    }

    for item in dados:
        idade = item["age_years"]

        if idade <= 2:
            faixas["0–2 anos"] += 1

        elif idade <= 5:
            faixas["3–5 anos"] += 1

        elif idade <= 8:
            faixas["6–8 anos"] += 1

        elif idade <= 11:
            faixas["9–11 anos"] += 1

        elif idade <= 15:
            faixas["12–15 anos"] += 1

        else:
            faixas["Mais de 15 anos"] += 1

    categorias = list(
        faixas.keys()
    )

    quantidades = list(
        faixas.values()
    )

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    barras = ax.bar(
        categorias,
        quantidades
    )

    ax.set_title(
        "RQ01 — Distribuição da Idade dos Repositórios"
    )

    ax.set_xlabel(
        "Idade do repositório"
    )

    ax.set_ylabel(
        "Quantidade de repositórios"
    )

    ax.tick_params(
        axis="x",
        rotation=20
    )

    for barra in barras:
        altura = barra.get_height()

        ax.text(
            barra.get_x()
            + barra.get_width() / 2,
            altura,
            str(int(altura)),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(
        GRAFICO_RQ01,
        dpi=150
    )

    plt.close(fig)

    return faixas


def gerar_grafico_rq02(dados):
    faixas = {
        "0 PRs": 0,
        "1–10": 0,
        "11–100": 0,
        "101–1.000": 0,
        "1.001–10.000": 0,
        "Mais de 10.000": 0
    }

    for item in dados:
        prs = item[
            "merged_pull_requests"
        ]

        if prs == 0:
            faixas["0 PRs"] += 1

        elif prs <= 10:
            faixas["1–10"] += 1

        elif prs <= 100:
            faixas["11–100"] += 1

        elif prs <= 1000:
            faixas["101–1.000"] += 1

        elif prs <= 10000:
            faixas["1.001–10.000"] += 1

        else:
            faixas[
                "Mais de 10.000"
            ] += 1

    categorias = list(
        faixas.keys()
    )

    quantidades = list(
        faixas.values()
    )

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    barras = ax.bar(
        categorias,
        quantidades
    )

    ax.set_title(
        "RQ02 — Distribuição de Pull Requests Aceitas"
    )

    ax.set_xlabel(
        "Quantidade de Pull Requests aceitas"
    )

    ax.set_ylabel(
        "Quantidade de repositórios"
    )

    ax.tick_params(
        axis="x",
        rotation=20
    )

    for barra in barras:
        altura = barra.get_height()

        ax.text(
            barra.get_x()
            + barra.get_width() / 2,
            altura,
            str(int(altura)),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(
        GRAFICO_RQ02,
        dpi=150
    )

    plt.close(fig)

    return faixas


def calcular_resumo(
    dados,
    faixas_rq01,
    faixas_rq02
):
    idades = [
        item["age_years"]
        for item in dados
    ]

    prs = [
        item["merged_pull_requests"]
        for item in dados
    ]

    idades_ordenadas = sorted(
        idades
    )

    prs_ordenadas = sorted(
        prs
    )

    meio = len(dados) // 2

    mediana_idade = (
        idades_ordenadas[meio]
    )

    mediana_prs = (
        prs_ordenadas[meio]
    )

    return {
        "total_repositorios":
            len(dados),

        "rq01": {
            "idade_minima":
                round(min(idades), 2),

            "idade_maxima":
                round(max(idades), 2),

            "idade_media":
                round(
                    sum(idades)
                    / len(idades),
                    2
                ),

            "idade_mediana":
                round(
                    mediana_idade,
                    2
                ),

            "distribuicao":
                faixas_rq01
        },

        "rq02": {
            "prs_minimo":
                min(prs),

            "prs_maximo":
                max(prs),

            "prs_media":
                round(
                    sum(prs)
                    / len(prs),
                    2
                ),

            "prs_mediana":
                mediana_prs,

            "distribuicao":
                faixas_rq02
        }
    }


def salvar_resumo(
    resumo
):
    with open(
        SUMMARY_JSON,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resumo,
            arquivo,
            indent=2,
            ensure_ascii=False
        )


def main():
    print("=" * 60)
    print(
        "GRÁFICOS — RQ01 E RQ02"
    )
    print("=" * 60)

    dados = carregar_dados()

    if not dados:
        raise Exception(
            "Nenhum dado válido encontrado."
        )

    faixas_rq01 = gerar_grafico_rq01(
        dados
    )

    faixas_rq02 = gerar_grafico_rq02(
        dados
    )

    resumo = calcular_resumo(
        dados,
        faixas_rq01,
        faixas_rq02
    )

    salvar_resumo(
        resumo
    )

    print()
    print(
        "RQ01 — Distribuição por idade:"
    )

    for faixa, quantidade in (
        faixas_rq01.items()
    ):
        print(
            f"  {faixa}: "
            f"{quantidade}"
        )

    print()
    print(
        "RQ02 — Distribuição de PRs aceitas:"
    )

    for faixa, quantidade in (
        faixas_rq02.items()
    ):
        print(
            f"  {faixa}: "
            f"{quantidade}"
        )

    print()
    print(
        "Arquivos gerados:"
    )

    print(
        f"  {GRAFICO_RQ01}"
    )

    print(
        f"  {GRAFICO_RQ02}"
    )

    print(
        f"  {SUMMARY_JSON}"
    )


if __name__ == "__main__":
    main()