import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO_TRIALS = RAIZ / "dados" / "resultados_trials.csv"
ARQUIVO_METRICAS = RAIZ / "dados" / "metricas_estaticas.csv"
PASTA_GRAFICOS = RAIZ / "graficos"

PALETA = {"COM_IA": "#2e7d32", "SEM_IA": "#c62828"}


def carregar_dados():
    trials = pd.read_csv(ARQUIVO_TRIALS)
    metricas = pd.read_csv(ARQUIVO_METRICAS)
    return trials, metricas


def grafico_tempo(trials):
    figura, eixo = plt.subplots(figsize=(8, 5))

    sns.boxplot(
        data=trials,
        x="tratamento",
        y="tempo_minutos",
        hue="tratamento",
        palette=PALETA,
        showfliers=False,
        ax=eixo,
        legend=False,
    )
    sns.stripplot(
        data=trials,
        x="tratamento",
        y="tempo_minutos",
        color="black",
        size=7,
        jitter=True,
        alpha=0.7,
        ax=eixo,
    )

    eixo.set_title("RQ1 — Time-to-green por tratamento")
    eixo.set_xlabel("Tratamento")
    eixo.set_ylabel("Tempo (minutos)")
    eixo.set_yscale("log")

    figura.tight_layout()
    figura.savefig(PASTA_GRAFICOS / "rq1_tempo_por_tratamento.png", dpi=150)
    plt.close(figura)


def grafico_taxa_sucesso(trials):
    figura, eixo = plt.subplots(figsize=(8, 5))

    resumo = (
        trials.groupby(["kata", "tratamento"])["taxa_sucesso_percentual"]
        .mean()
        .reset_index()
    )

    sns.barplot(
        data=resumo,
        x="kata",
        y="taxa_sucesso_percentual",
        hue="tratamento",
        palette=PALETA,
        ax=eixo,
    )

    eixo.set_ylim(90, 102)
    eixo.set_title("RQ2 — Taxa de sucesso dos testes por kata e tratamento")
    eixo.set_xlabel("Kata")
    eixo.set_ylabel("Taxa de sucesso média (%)")
    eixo.legend(title="Tratamento")

    figura.tight_layout()
    figura.savefig(PASTA_GRAFICOS / "rq2_taxa_sucesso_por_kata.png", dpi=150)
    plt.close(figura)


def grafico_metricas(metricas):
    figura, eixos = plt.subplots(1, 3, figsize=(15, 5))

    graficos = [
        ("complexidade_ciclomatica_media", "RQ3 — CC média", "CC média"),
        ("maintainability_index", "RQ3 — Maintainability Index", "MI"),
        ("loc", "Controle — LOC", "LOC"),
    ]

    for eixo, (campo, titulo, rotulo_y) in zip(eixos, graficos):
        sns.boxplot(
            data=metricas,
            x="tratamento",
            y=campo,
            hue="tratamento",
            palette=PALETA,
            showfliers=False,
            ax=eixo,
            legend=False,
        )
        sns.stripplot(
            data=metricas,
            x="tratamento",
            y=campo,
            color="black",
            size=7,
            jitter=True,
            alpha=0.7,
            ax=eixo,
        )
        eixo.set_title(titulo)
        eixo.set_xlabel("Tratamento")
        eixo.set_ylabel(rotulo_y)

    figura.tight_layout()
    figura.savefig(PASTA_GRAFICOS / "rq3_metricas_por_tratamento.png", dpi=150)
    plt.close(figura)


def grafico_correlacao(metricas):
    colunas = [
        "loc",
        "complexidade_ciclomatica_media",
        "maintainability_index",
        "duplicacao_percentual",
    ]
    rotulos = {
        "loc": "LOC",
        "complexidade_ciclomatica_media": "CC média",
        "maintainability_index": "MI",
        "duplicacao_percentual": "Duplicação %",
    }

    correlacao = metricas[colunas].corr(method="spearman")
    correlacao = correlacao.rename(index=rotulos, columns=rotulos)

    figura, eixo = plt.subplots(figsize=(7, 6))
    sns.heatmap(
        correlacao,
        annot=True,
        fmt=".2f",
        cmap="vlag",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        ax=eixo,
    )
    eixo.set_title("Correlação entre métricas estáticas (Spearman)")

    figura.tight_layout()
    figura.savefig(PASTA_GRAFICOS / "correlacao_metricas.png", dpi=150)
    plt.close(figura)


def grafico_scatter(metricas):
    figura, eixo = plt.subplots(figsize=(8, 5.5))

    sns.scatterplot(
        data=metricas,
        x="loc",
        y="complexidade_ciclomatica_media",
        hue="tratamento",
        palette=PALETA,
        s=90,
        ax=eixo,
    )

    for _, linha in metricas.iterrows():
        eixo.annotate(
            f"{linha['participante']}\n{linha['kata']}",
            (linha["loc"], linha["complexidade_ciclomatica_media"]),
            textcoords="offset points",
            xytext=(8, 4),
            fontsize=7,
            alpha=0.8,
        )

    eixo.set_title("RQ3 — Complexidade ciclomática versus LOC")
    eixo.set_xlabel("LOC")
    eixo.set_ylabel("CC média")

    figura.tight_layout()
    figura.savefig(PASTA_GRAFICOS / "rq3_cc_por_loc.png", dpi=150)
    plt.close(figura)


def main():
    trials, metricas = carregar_dados()
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    grafico_tempo(trials)
    grafico_taxa_sucesso(trials)
    grafico_metricas(metricas)
    grafico_correlacao(metricas)
    grafico_scatter(metricas)

    print(f"Gráficos gerados em: {PASTA_GRAFICOS}")


if __name__ == "__main__":
    main()