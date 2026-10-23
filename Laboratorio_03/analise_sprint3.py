"""Gera as análises reprodutíveis das RQ01--RQ07 a partir do dataset final.

Uso: python analise_sprint3.py

Os resultados são gravados em ``resultados/sprint3``. A análise usa somente
arquivos versionados do diretório ``resultados`` e não faz chamadas à API.
"""
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, spearmanr


ROOT = Path(__file__).parent
RESULTS = ROOT / "resultados"
OUT = RESULTS / "sprint3"
OUT.mkdir(exist_ok=True)


def numeric(df, column):
    return pd.to_numeric(df[column], errors="coerce")


def summary(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    return {
        "n": int(s.size),
        "missing": int(series.size - s.size),
        "median": None if s.empty else float(s.median()),
        "q1": None if s.empty else float(s.quantile(.25)),
        "q3": None if s.empty else float(s.quantile(.75)),
        "iqr": None if s.empty else float(s.quantile(.75) - s.quantile(.25)),
    }


def dora_frequency(value):
    if pd.isna(value):
        return None
    if value >= 7:
        return "Elite"
    if value >= 1:
        return "High"
    if value >= 1 / 4.345:
        return "Medium"
    return "Low"


def dora_lead(value):
    if pd.isna(value):
        return None
    if value < 24:
        return "Elite"
    if value < 24 * 7:
        return "High"
    if value < 24 * 30:
        return "Medium"
    return "Low"


def dora_cfr(value):
    if pd.isna(value):
        return None
    if value <= .15:
        return "Elite"
    if value <= .30:
        return "High"
    if value <= .45:
        return "Medium"
    return "Low"


def dora_recovery(value):
    if pd.isna(value):
        return None
    if value < 1:
        return "Elite"
    if value < 24:
        return "High"
    if value < 24 * 7:
        return "Medium"
    return "Low"


def score(category):
    return {"Low": 1, "Medium": 2, "High": 3, "Elite": 4}.get(category)


def classify(df, frequency, lead, cfr, recovery):
    funcs = {
        "deployment_frequency_semana": dora_frequency,
        "lead_time_release_horas": dora_lead,
        "lead_time_commit_horas": dora_lead,
        "cfr_ci": dora_cfr,
        "cfr_entrega": dora_cfr,
        "recuperacao_horas": dora_recovery,
    }
    cols = [frequency, lead, cfr, recovery]
    names = [f"{c}_classe" for c in cols]
    result = pd.DataFrame(index=df.index)
    for col, name in zip(cols, names):
        result[name] = numeric(df, col).map(funcs[col])
    result["classe_geral"] = result[names].apply(
        lambda row: {1: "Low", 2: "Medium", 3: "High", 4: "Elite"}.get(
            math.floor(np.median([score(x) for x in row if pd.notna(x) and score(x) is not None]))
        ) if any(pd.notna(x) and score(x) is not None for x in row) else None,
        axis=1,
    )
    return result


ORDEM = ["Elite", "High", "Medium", "Low"]
ORDEM_KAPPA = ["Low", "Medium", "High", "Elite"]
CORES = {
    "Elite": "#1b7f4e",
    "High": "#2f6f9f",
    "Medium": "#d4a017",
    "Low": "#b5523a",
}
AZUL = "#1f4e79"


def estilo():
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.28,
        "grid.linestyle": "--",
        "axes.axisbelow": True,
    })


def salvar(fig, filename):
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def histograma(series, title, xlabel, filename, log=False, linhas=None):
    s = pd.to_numeric(series, errors="coerce").dropna()
    s = s[s > 0] if log else s
    if s.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 4.4))
    if log:
        bins = np.logspace(np.log10(s.min() * 0.9), np.log10(s.max() * 1.05), 28)
        ax.hist(s, bins=bins, color=AZUL, alpha=0.9)
        ax.set_xscale("log")
    else:
        ax.hist(s, bins=24, color=AZUL, alpha=0.9, range=(0, max(1, float(s.max()))))
    ax.axvline(s.median(), color="#c0392b", linewidth=1.6, label=f"mediana = {s.median():.3g}")
    for valor, nome in linhas or []:
        ax.axvline(valor, color="#5c6b73", linewidth=1, linestyle=":", label=nome)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Repositórios")
    ax.legend(frameon=False, fontsize=9)
    salvar(fig, filename)


def dispersao(df, cfr, titulo, filename):
    valid = df[["deployment_frequency_semana", cfr]].apply(pd.to_numeric, errors="coerce").dropna()
    valid = valid[valid.iloc[:, 0] > 0]
    rho, p = spearmanr(valid.iloc[:, 0], valid.iloc[:, 1])
    p_txt = "p < 0,001" if p < 0.001 else f"p = {p:.3f}".replace(".", ",")
    rho_txt = f"{rho:.2f}".replace(".", ",")
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.scatter(valid.iloc[:, 0], valid.iloc[:, 1] * 100, s=28, alpha=0.55,
               color=AZUL, edgecolors="white", linewidths=0.4)
    ax.set_xscale("log")
    ax.set_xlabel("Releases por semana (escala log)")
    ax.set_ylabel("Change failure rate (%)")
    ax.set_title(f"{titulo}\nSpearman ρ = {rho_txt}, {p_txt}, n = {len(valid)}")
    salvar(fig, filename)
    return {"cfr": cfr, "n": len(valid), "rho": float(rho), "p_valor": float(p)}


def barras_empilhadas(tabela, titulo, filename, xlabel):
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    y = np.arange(len(tabela))
    esquerda = np.zeros(len(tabela))
    for classe in ORDEM:
        valores = tabela[classe].to_numpy()
        ax.barh(y, valores, left=esquerda, color=CORES[classe], label=classe, height=0.72)
        esquerda += valores
    faltam = tabela.sum(axis=1).max() - tabela.sum(axis=1)
    if float(faltam.max()) > 0:
        ax.barh(y, faltam.to_numpy(), left=esquerda, color="#d0d5d8", label="Sem episódio", height=0.72)
    ax.set_yticks(y)
    ax.set_yticklabels(tabela.index)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(titulo)
    ax.legend(ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    ax.grid(axis="y", visible=False)
    salvar(fig, filename)


def figura_idade(df):
    idade = numeric(df, "idade_dias")
    grupos = pd.qcut(idade, 4, labels=["Q1 novos", "Q2", "Q3", "Q4 antigos"])
    paineis = [
        ("deployment_frequency_semana", "Releases por semana", False),
        ("lead_time_release_horas", "Lead time por release (horas)", True),
        ("cfr_entrega", "CFR de entrega", False),
    ]
    fig, eixos = plt.subplots(1, 3, figsize=(11.2, 4.2))
    for ax, (coluna, ylabel, log) in zip(eixos, paineis):
        dados = [numeric(df, coluna)[grupos == rotulo].dropna() for rotulo in grupos.cat.categories]
        ax.boxplot(
            dados, showfliers=False, patch_artist=True,
            medianprops={"color": "#c0392b", "linewidth": 1.6},
            boxprops={"facecolor": "#d6e4f0", "edgecolor": AZUL},
            whiskerprops={"color": AZUL}, capprops={"color": AZUL},
        )
        ax.set_xticks(range(1, len(dados) + 1), list(grupos.cat.categories))
        if log:
            ax.set_yscale("log")
        ax.set_ylabel(ylabel)
        ax.grid(axis="x", visible=False)
    fig.suptitle("RQ06 — métricas por quartil de idade do repositório", fontsize=13, fontweight="bold")
    salvar(fig, "rq06_idade.png")


def figura_linguagem(df):
    lingua = df["linguagem"].fillna("Não informado")
    frequencia = numeric(df, "deployment_frequency_semana")
    contagem = lingua.value_counts()
    escolhidas = contagem[contagem >= 10].index
    resumo = (
        pd.DataFrame({"linguagem": lingua, "frequencia": frequencia})
        .loc[lambda t: t["linguagem"].isin(escolhidas)]
        .groupby("linguagem")["frequencia"]
        .median()
        .sort_values()
    )
    rotulos = [f"{nome} ({int(contagem[nome])})" for nome in resumo.index]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.barh(rotulos, resumo.values, color=AZUL)
    ax.set_xlabel("Mediana de releases por semana")
    ax.set_title("RQ06 — frequência por linguagem (10 ou mais repositórios)")
    ax.grid(axis="y", visible=False)
    salvar(fig, "rq06_linguagem.png")


def gerar_figuras(df, classes, por_metrica):
    estilo()
    histograma(
        df["deployment_frequency_semana"], "RQ01 — Frequência de deploy",
        "Releases por semana (escala log)", "rq01_frequency.png", log=True,
        linhas=[(1 / 4.345, "1 por mês"), (1, "1 por semana"), (7, "7 por semana")],
    )
    histograma(
        df["lead_time_release_horas"], "RQ02 — Lead time por release",
        "Horas (escala log)", "rq02_lead_release.png", log=True,
        linhas=[(24, "1 dia"), (24 * 7, "1 semana"), (24 * 30, "30 dias")],
    )
    histograma(
        df["lead_time_commit_horas"], "RQ02 — Lead time por commit",
        "Horas (escala log)", "rq02_lead_commit.png", log=True,
        linhas=[(24, "1 dia"), (24 * 7, "1 semana"), (24 * 30, "30 dias")],
    )
    histograma(
        df["cfr_ci"], "RQ03 — CFR de CI", "Proporção de runs com falha",
        "rq03_cfr_ci.png", linhas=[(0.15, "15%"), (0.30, "30%"), (0.45, "45%")],
    )
    histograma(
        df["cfr_entrega"], "RQ03 — CFR de entrega", "Proporção de releases com correção em 7 dias",
        "rq03_cfr_entrega.png", linhas=[(0.15, "15%"), (0.30, "30%"), (0.45, "45%")],
    )
    histograma(
        df["recuperacao_horas"], "RQ04 — Tempo de recuperação",
        "Horas (escala log)", "rq04_recovery.png", log=True,
        linhas=[(1, "1 hora"), (24, "1 dia"), (24 * 7, "1 semana")],
    )
    correlacoes = [
        dispersao(df, "cfr_ci", "RQ05 — frequência × CFR de CI", "rq05_cfr_ci.png"),
        dispersao(df, "cfr_entrega", "RQ05 — frequência × CFR de entrega", "rq05_cfr_entrega.png"),
    ]
    pd.DataFrame(correlacoes).to_csv(OUT / "rq05_correlacoes.csv", index=False)

    geral = pd.DataFrame({nome: classes[nome].value_counts() for nome in ["C1", "C2", "C3"]}).T
    geral = geral.reindex(columns=ORDEM).fillna(0).astype(int)
    barras_empilhadas(geral, "RQ07 — classificação geral nas três combinações",
                      "rq07_classificacao.png", "Repositórios")
    barras_empilhadas(por_metrica, "Classificação DORA de cada métrica",
                      "rq_classificacao_metricas.png", "Repositórios")
    figura_idade(df)
    figura_linguagem(df)


def anexar_consenso(df):
    caminho = ROOT / "validacao" / "consenso_repositorios.csv"
    if not caminho.exists():
        return df
    consenso = pd.read_csv(caminho)
    base = df.drop(columns=["tipo_projeto_consenso", "entregas_reais_consenso"], errors="ignore")
    return base.merge(
        consenso[["repositorio", "tipo_projeto", "entregas_reais"]],
        on="repositorio", how="left",
    ).rename(columns={
        "tipo_projeto": "tipo_projeto_consenso",
        "entregas_reais": "entregas_reais_consenso",
    })


def classes_por_metrica(df):
    series = {
        "Frequência": numeric(df, "deployment_frequency_semana").map(dora_frequency),
        "Lead time por release": numeric(df, "lead_time_release_horas").map(dora_lead),
        "CFR de CI": numeric(df, "cfr_ci").map(dora_cfr),
        "CFR de entrega": numeric(df, "cfr_entrega").map(dora_cfr),
        "Recuperação": numeric(df, "recuperacao_horas").map(dora_recovery),
    }
    tabela = pd.DataFrame({nome: s.value_counts() for nome, s in series.items()}).T
    return tabela.reindex(columns=ORDEM).fillna(0).astype(int)


def main():
    from sklearn.metrics import cohen_kappa_score
    from statsmodels.stats.multitest import multipletests

    df = anexar_consenso(pd.read_csv(RESULTS / "dataset_final.csv"))
    summaries = {
        "RQ01_deployment_frequency": summary(df["deployment_frequency_semana"]),
        "RQ02_lead_time_release": summary(df["lead_time_release_horas"]),
        "RQ02_lead_time_commit": summary(df["lead_time_commit_horas"]),
        "RQ03_cfr_ci": summary(df["cfr_ci"]),
        "RQ03_cfr_entrega": summary(df["cfr_entrega"]),
        "RQ04_recuperacao": summary(df["recuperacao_horas"]),
    }
    (OUT / "estatistica_descritiva.json").write_text(
        json.dumps(summaries, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pd.DataFrame(summaries).T.reset_index(names="metrica").to_csv(
        OUT / "estatistica_descritiva.csv", index=False
    )

    c1 = classify(df, "deployment_frequency_semana", "lead_time_release_horas", "cfr_ci", "recuperacao_horas")
    c2 = classify(df, "deployment_frequency_semana", "lead_time_commit_horas", "cfr_entrega", "recuperacao_horas")
    c3 = classify(df, "deployment_frequency_semana", "lead_time_release_horas", "cfr_entrega", "recuperacao_horas")
    classes = pd.DataFrame({
        "repositorio": df["repositorio"],
        "C1": c1["classe_geral"],
        "C2": c2["classe_geral"],
        "C3": c3["classe_geral"],
    })
    classes.to_csv(OUT / "classificacoes_dora.csv", index=False)
    por_metrica = classes_por_metrica(df)
    por_metrica.to_csv(OUT / "classificacao_por_metrica.csv")

    comparisons = []
    for a, b in [("C1", "C2"), ("C1", "C3"), ("C2", "C3")]:
        valid = classes[[a, b]].dropna()
        comparisons.append({
            "configuracao_a": a,
            "configuracao_b": b,
            "n": len(valid),
            "mudaram_categoria": int((valid[a] != valid[b]).sum()),
            "percentual_mudanca": float((valid[a] != valid[b]).mean() * 100) if len(valid) else None,
            "kappa_ponderado": float(cohen_kappa_score(
                valid[a], valid[b], labels=ORDEM_KAPPA, weights="linear"
            )) if len(valid) else None,
        })
    pd.DataFrame(comparisons).to_csv(OUT / "rq07_sensibilidade.csv", index=False)

    metrics = [
        "deployment_frequency_semana", "lead_time_release_horas", "lead_time_commit_horas",
        "cfr_ci", "cfr_entrega", "recuperacao_horas",
    ]
    factors = {
        "linguagem": df["linguagem"].fillna("Não informado"),
        "quartil_estrelas": pd.qcut(numeric(df, "estrelas"), 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"),
        "quartil_idade": pd.qcut(numeric(df, "idade_dias"), 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"),
    }
    if df["tipo_projeto_consenso"].fillna("").ne("").any():
        factors["tipo_projeto"] = df["tipo_projeto_consenso"].replace("", np.nan)
    tests = []
    for factor, groups in factors.items():
        for metric in metrics:
            tmp = pd.DataFrame({"group": groups, "value": numeric(df, metric)}).dropna()
            partes = [(str(g), sub["value"].to_numpy()) for g, sub in tmp.groupby("group", observed=True) if len(sub) >= 2]
            if len(partes) < 2:
                continue
            names, arrays = zip(*partes)
            if len(arrays) == 2:
                stat, p = mannwhitneyu(arrays[0], arrays[1], alternative="two-sided")
                n1, n2 = len(arrays[0]), len(arrays[1])
                effect = 2 * stat / (n1 * n2) - 1
                effect_name = "cliffs_delta"
                test_name = "Mann-Whitney"
            else:
                stat, p = kruskal(*arrays)
                effect = stat / (len(tmp) - 1)
                effect_name = "epsilon_squared"
                test_name = "Kruskal-Wallis"
            tests.append({
                "fator": factor, "metrica": metric, "teste": test_name,
                "grupos": "|".join(names), "n": len(tmp), "estatistica": stat,
                "p_valor": p, effect_name: effect,
            })
    tests_df = pd.DataFrame(tests)
    if not tests_df.empty:
        tests_df["p_holm"] = multipletests(tests_df["p_valor"], method="holm")[1]
        tests_df["significativo_05"] = tests_df["p_holm"] < .05
    tests_df.to_csv(OUT / "rq06_testes.csv", index=False)
    gerar_figuras(df, classes, por_metrica)
    (OUT / "LEIA-ME.md").write_text(
        "# Resultados da Sprint 3\n\n"
        "Tabelas e figuras geradas por `python analise_sprint3.py` a partir de "
        "`resultados/dataset_final.csv` e `validacao/consenso_repositorios.csv`.\n\n"
        "Combinações da classificação geral:\n\n"
        "- C1: frequência, lead time por release, CFR de CI e tempo de recuperação.\n"
        "- C2: frequência, lead time por commit, CFR de entrega e tempo de recuperação.\n"
        "- C3: frequência, lead time por release, CFR de entrega e tempo de recuperação.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
