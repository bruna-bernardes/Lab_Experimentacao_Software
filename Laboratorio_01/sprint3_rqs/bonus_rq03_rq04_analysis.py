import csv
import json
import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(LAB_DIR, "data")
EXTRAS_DIR = os.path.join(LAB_DIR, "data_extras")

os.makedirs(EXTRAS_DIR, exist_ok=True)

REPOS_CSV = os.path.join(DATA_DIR, "repositorios_1000.csv")

SUMMARY_JSON = os.path.join(EXTRAS_DIR, "bonus_rq03_rq04_summary.json")
GRAFICO_RQ03 = os.path.join(EXTRAS_DIR, "bonus_rq03_estrelas_releases.png")
GRAFICO_RQ04 = os.path.join(EXTRAS_DIR, "bonus_rq04_distribuicao_atualizacao.png")

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
                estrelas = int(row["stars"])
                releases = int(row["total_releases"])

                updated_at = row.get(
                    "updated_at",
                    ""
                ).strip()

                if not updated_at:
                    ignorados += 1
                    continue

                data_atualizacao = datetime.fromisoformat(
                    updated_at.replace(
                        "Z",
                        "+00:00"
                    )
                )

                dias_desde_atualizacao = (
                    agora - data_atualizacao
                ).days

                if dias_desde_atualizacao < 0:
                    ignorados += 1
                    continue

                dados.append({
                    "repository": row["repository"],
                    "stars": estrelas,
                    "total_releases": releases,
                    "days_since_last_update":
                        dias_desde_atualizacao
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


def interpretar_correlacao(
    rho,
    p_value,
    metrica
):
    if p_value >= 0.05:
        return (
            "Não foi identificada correlação "
            "estatisticamente significativa."
        )

    valor = abs(rho)

    if valor < 0.3:
        forca = "fraca"
    elif valor < 0.6:
        forca = "moderada"
    else:
        forca = "forte"

    if metrica == "releases":
        if rho > 0:
            sentido = (
                "repositórios com mais estrelas "
                "tendem a possuir mais releases"
            )
        else:
            sentido = (
                "repositórios com mais estrelas "
                "tendem a possuir menos releases"
            )

    else:
        if rho < 0:
            sentido = (
                "repositórios com mais estrelas "
                "tendem a ter atualizações mais recentes"
            )
        else:
            sentido = (
                "repositórios com mais estrelas "
                "tendem a apresentar maior tempo "
                "desde a última atualização"
            )

    return (
        f"Foi encontrada uma correlação {forca}. "
        f"Os resultados indicam que {sentido}."
    )


def analisar_rq03(dados):
    estrelas = [
        item["stars"]
        for item in dados
    ]

    releases = [
        item["total_releases"]
        for item in dados
    ]

    rho, p_value = stats.spearmanr(
        estrelas,
        releases
    )

    return {
        "analise":
            "Estrelas x Total de Releases",

        "total_repositorios":
            len(dados),

        "spearman_rho":
            round(float(rho), 4),

        "p_value":
            round(float(p_value), 6),

        "significativo_5pct":
            bool(p_value < 0.05),

        "interpretacao":
            interpretar_correlacao(
                rho,
                p_value,
                "releases"
            )
    }


def analisar_rq04(dados):
    estrelas = [
        item["stars"]
        for item in dados
    ]

    dias = [
        item["days_since_last_update"]
        for item in dados
    ]

    rho, p_value = stats.spearmanr(
        estrelas,
        dias
    )

    return {
        "analise":
            "Estrelas x Dias desde última atualização",

        "total_repositorios":
            len(dados),

        "spearman_rho":
            round(float(rho), 4),

        "p_value":
            round(float(p_value), 6),

        "significativo_5pct":
            bool(p_value < 0.05),

        "interpretacao":
            interpretar_correlacao(
                rho,
                p_value,
                "atualizacao"
            )
    }


def gerar_grafico_rq03(dados):
    estrelas = [
        item["stars"]
        for item in dados
    ]

    releases = [
        item["total_releases"]
        for item in dados
    ]

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    ax.scatter(
        estrelas,
        releases,
        alpha=0.4,
        s=15
    )

    ax.set_xscale("log")
    ax.set_yscale("symlog") 
    ax.set_ylim(bottom=0)
    
    ax.set_xlabel(
        "Número de estrelas (escala log)"
    )

    ax.set_ylabel(
        "Total de releases"
    )

    ax.set_title(
        "RQ03 Extra — Estrelas x Total de Releases"
    )

    plt.tight_layout()

    plt.savefig(
        GRAFICO_RQ03,
        dpi=150
    )

    plt.close(fig)

    return GRAFICO_RQ03


def gerar_grafico_rq04(dados):
    faixas = {
        "0 dias": 0,
        "1–7 dias": 0,
        "8–30 dias": 0,
        "31–90 dias": 0,
        "91–365 dias": 0,
        "Mais de 365 dias": 0
    }

    for item in dados:
        dias = item["days_since_last_update"]

        if dias == 0:
            faixas["0 dias"] += 1

        elif dias <= 7:
            faixas["1–7 dias"] += 1

        elif dias <= 30:
            faixas["8–30 dias"] += 1

        elif dias <= 90:
            faixas["31–90 dias"] += 1

        elif dias <= 365:
            faixas["91–365 dias"] += 1

        else:
            faixas["Mais de 365 dias"] += 1

    categorias = list(faixas.keys())
    quantidades = list(faixas.values())

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    barras = ax.bar(
        categorias,
        quantidades
    )

    ax.set_xlabel(
        "Tempo desde a última atualização"
    )

    ax.set_ylabel(
        "Quantidade de repositórios"
    )

    ax.set_title(
        "RQ04 Extra — Distribuição do Tempo desde a Última Atualização"
    )

    ax.tick_params(
        axis="x",
        rotation=20
    )

    # Mostra a quantidade acima de cada barra
    for barra in barras:
        altura = barra.get_height()

        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            str(int(altura)),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(
        GRAFICO_RQ04,
        dpi=150
    )

    plt.close(fig)

    return GRAFICO_RQ04

def gerar_texto_relatorio(
    rq03,
    rq04
):
    texto_rq03 = (
        "Na análise complementar da RQ03, "
        f"a correlação de Spearman entre número "
        f"de estrelas e total de releases foi "
        f"ρ={rq03['spearman_rho']} "
        f"(p={rq03['p_value']}). "
        f"{rq03['interpretacao']}"
    )

    texto_rq04 = (
        "Na análise complementar da RQ04, "
        f"a correlação de Spearman entre número "
        f"de estrelas e dias desde a última "
        f"atualização foi "
        f"ρ={rq04['spearman_rho']} "
        f"(p={rq04['p_value']}). "
        f"{rq04['interpretacao']}"
    )

    return (
        texto_rq03
        + "\n\n"
        + texto_rq04
    )


def salvar_resultados(
    rq03,
    rq04
):
    resultado = {
        "rq03_extra": rq03,
        "rq04_extra": rq04
    }

    with open(
        SUMMARY_JSON,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            resultado,
            arquivo,
            indent=2,
            ensure_ascii=False
        )


def main():
    print("=" * 60)
    print("ANÁLISE EXTRA — RQ03 E RQ04")
    print("=" * 60)

    dados = carregar_dados()

    if len(dados) < 2:
        raise Exception(
            "Amostra insuficiente para realizar as correlações."
        )

    rq03 = analisar_rq03(dados)
    rq04 = analisar_rq04(dados)

    print()
    print(
        "--- RQ03 EXTRA: "
        "Estrelas x Releases ---"
    )

    print(
        json.dumps(
            rq03,
            indent=2,
            ensure_ascii=False
        )
    )

    print()
    print(
        "--- RQ04 EXTRA: "
        "Estrelas x Atualização ---"
    )

    print(
        json.dumps(
            rq04,
            indent=2,
            ensure_ascii=False
        )
    )

    grafico_rq03 = gerar_grafico_rq03(
        dados
    )

    grafico_rq04 = gerar_grafico_rq04(
        dados
    )

    salvar_resultados(
        rq03,
        rq04
    )

    print()
    print("Gráficos gerados:")

    print(
        f"  {grafico_rq03}"
    )

    print(
        f"  {grafico_rq04}"
    )

    print()
    print(
        f"Resumo JSON: {SUMMARY_JSON}"
    )

    print()
    print("=" * 60)
    print(
        "TEXTO PARA O RELATÓRIO"
    )
    print("=" * 60)

    print(
        gerar_texto_relatorio(
            rq03,
            rq04
        )
    )


if __name__ == "__main__":
    main()