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
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.multitest import multipletests


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


def write_plot(series, title, ylabel, filename):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(s, bins=30, color="#2f6f9f", alpha=.85)
    ax.set_title(title)
    ax.set_ylabel("Repositórios")
    ax.set_xlabel(ylabel)
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=160)
    plt.close(fig)


def main():
    df = pd.read_csv(RESULTS / "dataset_final.csv")
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

    for col, title, label, file in [
        ("deployment_frequency_semana", "RQ01 — Deployment frequency", "releases/semana", "rq01_frequency.png"),
        ("lead_time_release_horas", "RQ02 — Lead time por release", "horas", "rq02_lead_release.png"),
        ("lead_time_commit_horas", "RQ02 — Lead time por commit", "horas", "rq02_lead_commit.png"),
        ("cfr_ci", "RQ03 — CFR por CI", "proporção", "rq03_cfr_ci.png"),
        ("cfr_entrega", "RQ03 — CFR por entrega", "proporção", "rq03_cfr_entrega.png"),
        ("recuperacao_horas", "RQ04 — Recuperação", "horas", "rq04_recovery.png"),
    ]:
        write_plot(df[col], title, label, file)

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

    comparisons = []
    for a, b in [("C1", "C2"), ("C1", "C3"), ("C2", "C3")]:
        valid = classes[[a, b]].dropna()
        comparisons.append({
            "configuracao_a": a,
            "configuracao_b": b,
            "n": len(valid),
            "mudaram_categoria": int((valid[a] != valid[b]).sum()),
            "percentual_mudanca": float((valid[a] != valid[b]).mean() * 100) if len(valid) else None,
            "kappa_ponderado": float(cohen_kappa_score(valid[a], valid[b], weights="linear")) if len(valid) else None,
        })
    pd.DataFrame(comparisons).to_csv(OUT / "rq07_sensibilidade.csv", index=False)

    correlations = []
    for cfr in ["cfr_ci", "cfr_entrega"]:
        valid = df[["deployment_frequency_semana", cfr]].apply(pd.to_numeric, errors="coerce").dropna()
        rho, p = spearmanr(valid.iloc[:, 0], valid.iloc[:, 1]) if len(valid) > 2 else (np.nan, np.nan)
        correlations.append({"cfr": cfr, "n": len(valid), "rho": rho, "p_valor": p})
        if len(valid):
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(valid.iloc[:, 0], valid.iloc[:, 1], alpha=.45, s=14)
            ax.set_xscale("log")
            ax.set_xlabel("Deployment frequency (releases/semana)")
            ax.set_ylabel(cfr)
            ax.set_title(f"RQ05 — frequência × {cfr}")
            fig.tight_layout()
            fig.savefig(OUT / f"rq05_{cfr}.png", dpi=160)
            plt.close(fig)
    pd.DataFrame(correlations).to_csv(OUT / "rq05_correlacoes.csv", index=False)

    metrics = {
        "deployment_frequency_semana": "frequência",
        "lead_time_release_horas": "lead time release",
        "lead_time_commit_horas": "lead time commit",
        "cfr_ci": "CFR CI",
        "cfr_entrega": "CFR entrega",
        "recuperacao_horas": "recuperação",
    }
    factors = {
        "linguagem": df["linguagem"].fillna("Não informado"),
        "quartil_estrelas": pd.qcut(numeric(df, "estrelas"), 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"),
        "quartil_idade": pd.qcut(numeric(df, "idade_dias"), 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"),
    }
    if "tipo_projeto_consenso" in df and df["tipo_projeto_consenso"].fillna("").ne("").any():
        fatores_tipo = df["tipo_projeto_consenso"].replace("", np.nan).fillna("não rotulado")
        fatores_tipo = fatores_tipo[fatores_tipo != "não rotulado"]
        factors["tipo_projeto"] = fatores_tipo
    tests = []
    for factor, groups in factors.items():
        for metric, label in metrics.items():
            tmp = pd.DataFrame({"group": groups, "value": numeric(df, metric)}).dropna()
            arrays = [g["value"].to_numpy() for _, g in tmp.groupby("group", observed=True) if len(g) >= 2]
            names = [str(g) for g, sub in tmp.groupby("group", observed=True) if len(sub) >= 2]
            if len(arrays) < 2:
                continue
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
    (OUT / "LEIA-ME.md").write_text(
        "# Resultados da Sprint 3\n\n"
        "Os CSVs e PNGs desta pasta foram gerados por `python analise_sprint3.py`.\n"
        "A RQ07 usa três combinações reprodutíveis dos campos disponíveis no dataset.\n"
        "A variante por tags não foi coletada nos resultados versionados e, por isso,\n"
        "não é apresentada como se tivesse sido observada.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
