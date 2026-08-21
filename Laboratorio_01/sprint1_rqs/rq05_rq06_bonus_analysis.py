import json
import os
import sys
 
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from scipy import stats
 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from Laboratorio_01.códigos.api_client import fetch_repos  
from Laboratorio_01.sprint1_rqs.rq05_languages import process_rq05, POPULAR_LANGUAGES_TIOBE
from Laboratorio_01.sprint1_rqs.rq06_issues import process_rq06
from Laboratorio_01.códigos.config import NUM_REPOS
 
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
 
 
def merge_rq05_rq06(repos):
    """
    Junta, por repositório, a linguagem primária (RQ05) com a
    razão de issues fechadas (RQ06), já reaproveitando o que os
    outros dois scripts calculam — sem duplicar lógica.
    """
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
        })
    return merged
 
 
def hypothesis_test_popular_vs_others(merged):
    """
    H0: repos em linguagem popular (TIOBE) e repos em outras
        linguagens vêm da mesma distribuição de closed_ratio.
    H1: as distribuições diferem.
 
    Usamos Mann-Whitney U (não-paramétrico) em vez de t-test porque
    closed_ratio é uma proporção limitada em [0,1] e não há garantia
    de normalidade — o próprio RQ06 já mostra distribuição assimétrica
    na maioria das amostras desse tipo de mineração.
    """
    popular = [r["closed_ratio"] for r in merged if r["primary_language"] in POPULAR_LANGUAGES_TIOBE]
    others = [r["closed_ratio"] for r in merged if r["primary_language"] not in POPULAR_LANGUAGES_TIOBE
              and r["primary_language"] != "None"]
 
    if len(popular) < 2 or len(others) < 2:
        return {"error": "Amostra insuficiente em um dos grupos para o teste."}
 
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
 
 
def correlation_stars_vs_closed_ratio(merged):
    """
    Correlação de Spearman (não assume relação linear nem normalidade)
    entre número de estrelas e proporção de issues fechadas.
    """
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
    """Boxplot do closed_ratio para as top_n linguagens mais frequentes."""
    from collections import Counter
    counts = Counter(r["primary_language"] for r in merged if r["primary_language"] != "None")
    top_langs = [lang for lang, _ in counts.most_common(top_n)]
 
    data = [[r["closed_ratio"] for r in merged if r["primary_language"] == lang] for lang in top_langs]
 
    fig, ax = plt.subplots(figsize=(10, 6))
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
    """Scatter estrelas x closed_ratio com linha de tendência (regressão linear simples)."""
    stars = [r["stars"] for r in merged]
    ratios = [r["closed_ratio"] for r in merged]
 
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(stars, ratios, alpha=0.4, s=15)
    ax.set_xscale("log")
    ax.set_xlabel("Estrelas (escala log)")
    ax.set_ylabel("Razão de issues fechadas")
    ax.set_title("Estrelas x Proporção de issues fechadas")
 
    # linha de tendência sobre log(stars)
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
 
 
def gerar_paragrafo_relatorio(hip_test, corr):
    if "error" in hip_test:
        return "Amostra insuficiente para o teste de hipótese bônus."
 
    sig = "houve diferença estatisticamente significativa" if hip_test["significativo_5pct"] else \
          "não houve diferença estatisticamente significativa"
 
    return (
        f"Como análise complementar às RQ05 e RQ06, testou-se se repositórios em linguagens "
        f"classificadas como populares pelo índice TIOBE (mediana de {hip_test['mediana_populares']} "
        f"na razão de issues fechadas, n={hip_test['n_populares']}) diferem dos repositórios em outras "
        f"linguagens (mediana de {hip_test['mediana_outras']}, n={hip_test['n_outras']}). Pelo teste de "
        f"Mann-Whitney U (U={hip_test['u_statistic']}, p={hip_test['p_value']}), {sig} ao nível de 5%. "
        f"Adicionalmente, a correlação de Spearman entre número de estrelas e razão de issues fechadas "
        f"foi de ρ={corr['spearman_rho']} (p={corr['p_value']}), indicando {corr['interpretacao']}."
    )
 
 
if __name__ == "__main__":
    repos = fetch_repos()
    merged = merge_rq05_rq06(repos)
 
    print("=" * 60)
    print("ANÁLISE EXTRA — RQ05 x RQ06 (linguagem popular x issues fechadas)")
    print("=" * 60)
 
    hip_test = hypothesis_test_popular_vs_others(merged)
    corr = correlation_stars_vs_closed_ratio(merged)
 
    print("\n--- Teste de hipótese (Mann-Whitney U) ---")
    print(json.dumps(hip_test, indent=2, ensure_ascii=False))
 
    print("\n--- Correlação estrelas x closed_ratio (Spearman) ---")
    print(json.dumps(corr, indent=2, ensure_ascii=False))
 
    box_path = plot_boxplot_por_linguagem(merged)
    scatter_path = plot_scatter_estrelas(merged)
    print(f"\nGráficos salvos em:\n  {box_path}\n  {scatter_path}")
 
    with open(os.path.join(DATA_DIR, "bonus_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "hypothesis_test_popular_vs_others": hip_test,
            "correlation_stars_vs_closed_ratio": corr,
        }, f, indent=2, ensure_ascii=False)
 
    print("\n--- Parágrafo pronto para o relatório ---\n")
    print(gerar_paragrafo_relatorio(hip_test, corr))