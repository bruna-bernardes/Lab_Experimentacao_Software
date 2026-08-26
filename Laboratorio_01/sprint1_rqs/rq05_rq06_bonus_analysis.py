import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(BASE_DIR)
CODIGOS_DIR = os.path.join(LAB_DIR, "códigos")
DATA_DIR = os.path.join(LAB_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

sys.path.insert(0, BASE_DIR)
if os.path.isdir(CODIGOS_DIR):
    sys.path.insert(0, CODIGOS_DIR)

from rq05_languages import POPULAR_LANGUAGES_TIOBE

REPOS_CSV = os.path.join(DATA_DIR, "repositorios_1000.csv")
RQ05_CSV = os.path.join(DATA_DIR, "rq05_languages.csv")
RQ06_CSV = os.path.join(DATA_DIR, "rq06_issues.csv")


from datetime import datetime, timezone

def load_from_repositorios_csv():
    if not os.path.exists(REPOS_CSV):
        return None

    merged = []
    ignoradas = 0
    
    agora = datetime.now(timezone.utc)

    with open(REPOS_CSV, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            lang = (row.get("primary_language") or "").strip() or "None"
            try:
                closed_ratio = float(row["closed_ratio"])
                stars = int(row["stars"])
                total_issues = int(row["total_issues"])
                total_releases = int(row.get("total_releases", 0))
                
                accepted_prs = int(row.get("merged_pull_requests", 0))
                
                updated_at_str = row.get("updated_at", "")
                if updated_at_str:
                    data_update = datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%SZ")
                    data_update = data_update.replace(tzinfo=timezone.utc)
                    diferenca = agora - data_update
                    days_since_last_update = diferenca.days
                else:
                    days_since_last_update = 0

            except (KeyError, ValueError):
                ignoradas += 1
                continue

            merged.append({
                "repository": row["repository"],
                "primary_language": lang,
                "closed_ratio": closed_ratio,
                "total_issues": total_issues,
                "stars": stars,
                "accepted_prs": accepted_prs,
                "total_releases": total_releases,
                "days_since_last_update": days_since_last_update,
            })

    if ignoradas:
        print(f"[dados] Aviso: {ignoradas} linha(s) ignorada(s).")
    return merged


def load_from_rq_csvs():
    if not (os.path.exists(RQ05_CSV) and os.path.exists(RQ06_CSV)):
        return None

    lang_by_repo = {}
    with open(RQ05_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lang_by_repo[row["repository"]] = row["primary_language"]

    merged = []
    with open(RQ06_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["repository"]
            merged.append({
                "repository": name,
                "primary_language": lang_by_repo.get(name, "None"),
                "closed_ratio": float(row["closed_ratio"]),
                "total_issues": int(row["total_issues"]),
                "stars": int(row["stars"]),
                "accepted_prs": 0,
                "total_releases": 0,
                "days_since_last_update": 0,
            })
    return merged


def load_from_api():
    from api_client import fetch_repos
    from rq05_languages import process_rq05
    from rq06_issues import process_rq06

    repos = fetch_repos()
    rq05 = process_rq05(repos)
    rq06 = process_rq06(repos)
    lang_by_repo = {r["repository"]: r["primary_language"] for r in rq05["results"]}

    merged = []
    for row in rq06["results"]:
        name = row["repository"]
        merged.append({
            "repository": name,
            "primary_language": lang_by_repo.get(name, "None"),
            "closed_ratio": row["closed_ratio"],
            "total_issues": row["total_issues"],
            "stars": row["stars"],
            "accepted_prs": row.get("accepted_prs", 0),
            "total_releases": row.get("total_releases", 0),
            "days_since_last_update": row.get("days_since_last_update", 0),
        })
    return merged


def get_merged_dataset():
    merged = load_from_repositorios_csv()
    if merged is not None:
        return merged
    merged = load_from_rq_csvs()
    if merged is not None:
        return merged
    return load_from_api()


def hypothesis_test_popular_vs_others(merged):
    popular = [r["closed_ratio"] for r in merged if r["primary_language"] in POPULAR_LANGUAGES_TIOBE]
    others = [r["closed_ratio"] for r in merged if r["primary_language"] not in POPULAR_LANGUAGES_TIOBE and r["primary_language"] != "None"]

    if len(popular) < 2 or len(others) < 2:
        return {"error": "Amostra insuficiente."}

    u_stat, p_value = stats.mannwhitneyu(popular, others, alternative="two-sided")

    return {
        "n_populares": len(popular),
        "n_outras": len(others),
        "mediana_populares": round(sorted(popular)[len(popular)//2], 4),
        "mediana_outras": round(sorted(others)[len(others)//2], 4),
        "u_statistic": round(float(u_stat), 4),
        "p_value": round(float(p_value), 6),
        "significativo_5pct": bool(p_value < 0.05),
    }


def hypothesis_test_rq07_completa(merged):
    populares = [r for r in merged if r["primary_language"] in POPULAR_LANGUAGES_TIOBE]
    outras = [r for r in merged if r["primary_language"] not in POPULAR_LANGUAGES_TIOBE and r["primary_language"] != "None"]

    metricas = {
        "accepted_prs": "PRs Aceitas (RQ02)",
        "total_releases": "Total de Releases (RQ03)",
        "days_since_last_update": "Dias desde a Última Atualização (RQ04)"
    }
    resultados = {}

    for campo, nome_display in metricas.items():
        vals_pop = [r.get(campo, 0) for r in populares]
        vals_out = [r.get(campo, 0) for r in outras]

        if len(vals_pop) >= 2 and len(vals_out) >= 2:
            u_stat, p_value = stats.mannwhitneyu(vals_pop, vals_out, alternative="two-sided")
            resultados[campo] = {
                "metrica": nome_display,
                "mediana_populares": sorted(vals_pop)[len(vals_pop)//2],
                "mediana_outras": sorted(vals_out)[len(vals_out)//2],
                "u_statistic": round(float(u_stat), 4),
                "p_value": round(float(p_value), 6),
                "significativo_5pct": bool(p_value < 0.05)
            }
        else:
            resultados[campo] = {"error": "Amostra insuficiente"}

    return resultados


def correlation_stars_vs_closed_ratio(merged):
    stars = [r["stars"] for r in merged]
    ratios = [r["closed_ratio"] for r in merged]
    rho, p_value = stats.spearmanr(stars, ratios)
    return {
        "spearman_rho": round(float(rho), 4),
        "p_value": round(float(p_value), 6),
        "interpretacao": interpretar_rho(rho, p_value),
    }


def interpretar_rho(rho, p_value):
    if p_value >= 0.05:
        return "sem correlação estatisticamente significativa"
    forca = "fraca" if abs(rho) < 0.3 else "moderada" if abs(rho) < 0.6 else "forte"
    direcao = "positiva" if rho > 0 else "negativa"
    return f"correlação {direcao} {forca} e estatisticamente significativa"


def plot_boxplot_por_linguagem(merged, top_n=8):
    from collections import Counter
    counts = Counter(r["primary_language"] for r in merged if r["primary_language"] != "None")
    top_langs = [lang for lang, _ in counts.most_common(top_n)]

    data = [[r["closed_ratio"] for r in merged if r["primary_language"] == lang] for lang in top_langs]

    fig, ax = plt.subplots(figsize=(10, 6))
    try:
        ax.boxplot(data, tick_labels=top_langs, showmeans=True)
    except TypeError:
        ax.boxplot(data, labels=top_langs, showmeans=True)
    ax.set_title(f"Distribuição da razão de issues fechadas — Top {top_n} linguagens")
    ax.set_ylabel("Issues fechadas / Total de issues")
    ax.set_xlabel("Linguagem primária")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    out_path = os.path.join(DATA_DIR, "bonus_boxplot_linguagens.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_scatter_estrelas(merged):
    stars = [r["stars"] for r in merged]
    ratios = [r["closed_ratio"] for r in merged]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(stars, ratios, alpha=0.4, s=15)
    ax.set_xscale("log")
    ax.set_xlabel("Estrelas (escala log)")
    ax.set_ylabel("Razão de issues fechadas")
    ax.set_title("Estrelas x Proporção de issues fechadas")

    import math
    log_stars = [math.log10(s) if s > 0 else 0 for s in stars]
    slope, intercept, *_ = stats.linregress(log_stars, ratios)
    xs = sorted(log_stars)
    ys = [slope * x + intercept for x in xs]
    ax.plot([10 ** x for x in xs], ys, color="red", linewidth=2, label="tendência")
    ax.legend()

    plt.tight_layout()
    out_path = os.path.join(DATA_DIR, "bonus_scatter_estrelas.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_rq07_boxplots(merged):
    populares = [r for r in merged if r["primary_language"] in POPULAR_LANGUAGES_TIOBE]
    outras = [r for r in merged if r["primary_language"] not in POPULAR_LANGUAGES_TIOBE and r["primary_language"] != "None"]

    metricas = {
        "accepted_prs": "PRs Aceitas (RQ02)",
        "total_releases": "Total de Releases (RQ03)",
        "days_since_last_update": "Dias desde a Última Atualização (RQ04)"
    }

    caminhos = []
    for campo, titulo in metricas.items():
        vals_pop = [r.get(campo, 0) for r in populares]
        vals_out = [r.get(campo, 0) for r in outras]

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.boxplot([vals_pop, vals_out], labels=["Populares", "Outras"], showmeans=True)
        ax.set_title(titulo)
        ax.set_ylabel("Quantidade (escala symlog)")
        ax.set_yscale("symlog") 
        
        plt.tight_layout()
        out_path = os.path.join(DATA_DIR, f"rq07_{campo}.png")
        plt.savefig(out_path, dpi=150)
        plt.close(fig)
        caminhos.append(out_path)
    
    return caminhos


def gerar_paragrafo_relatorio(hip_test, corr, rq07_test):
    texto = []
    if "error" not in hip_test:
        sig = "houve diferença significativa" if hip_test["significativo_5pct"] else "não houve diferença significativa"
        texto.append(
            f"Na análise (RQ06), repositórios em linguagens populares "
            f"(mediana {hip_test['mediana_populares']}) e outras linguagens (mediana {hip_test['mediana_outras']}) "
            f"foram comparados. O teste U (U={hip_test['u_statistic']}, p={hip_test['p_value']}) apontou que {sig}."
        )
    texto.append(
        f"A correlação de Spearman entre estrelas e issues fechadas "
        f"foi ρ={corr['spearman_rho']} (p={corr['p_value']}), indicando {corr['interpretacao']}."
    )
    if rq07_test and "error" not in rq07_test.get("accepted_prs", {}):
        texto.append(
            f"Para a RQ07, notou-se que repositórios populares têm mediana de {rq07_test['total_releases']['mediana_populares']} "
            f"releases contra {rq07_test['total_releases']['mediana_outras']} das demais linguagens "
            f"(p={rq07_test['total_releases']['p_value']})."
        )
    return "\n".join(texto)


if __name__ == "__main__":
    merged = get_merged_dataset()

    print("=" * 60)
    print("ANÁLISE EXTRA E CONSOLIDAÇÃO DA RQ07")
    print("=" * 60)

    hip_test = hypothesis_test_popular_vs_others(merged)
    corr = correlation_stars_vs_closed_ratio(merged)
    rq07_test = hypothesis_test_rq07_completa(merged)

    print("\n--- RQ06: Teste de hipótese Issues Fechadas (Mann-Whitney U) ---")
    print(json.dumps(hip_test, indent=2, ensure_ascii=False))

    print("\n--- Correlação Estrelas x Closed Ratio (Spearman) ---")
    print(json.dumps(corr, indent=2, ensure_ascii=False))

    print("\n--- RQ07: Comparação de PRs, Releases e Atualização (Mann-Whitney U) ---")
    print(json.dumps(rq07_test, indent=2, ensure_ascii=False))

    box_path = plot_boxplot_por_linguagem(merged)
    scatter_path = plot_scatter_estrelas(merged)
    graficos_rq07 = plot_rq07_boxplots(merged)
    
    print(f"\nGráficos salvos em:\n  {box_path}\n  {scatter_path}")
    print(f"Gráficos RQ07 salvos em:\n  {graficos_rq07}")

    with open(os.path.join(DATA_DIR, "bonus_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "hypothesis_test_popular_vs_others": hip_test,
            "correlation_stars_vs_closed_ratio": corr,
            "rq07_hypothesis_tests": rq07_test
        }, f, indent=2, ensure_ascii=False)

    print("\n--- Parágrafo pronto para o relatório ---\n")
    print(gerar_paragrafo_relatorio(hip_test, corr, rq07_test))