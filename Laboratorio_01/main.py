import json
import csv
import os
from rq01_age import process_rq01, validate_rq01
from rq02_pull_requests import process_rq02, validate_rq02
from rq03_releases import process_rq03, validate_rq03
from rq04_update_frequency import process_rq04, validate_rq04
from rq05_languages import process_rq05, validate_rq05, POPULAR_LANGUAGES_TIOBE
from rq06_issues import process_rq06, validate_rq06
from api_client import fetch_repos
from config import NUM_REPOS, VALIDATION_SAMPLE_SIZE

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def save_csv(filename, data, fieldnames):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Salvo: {filepath}")

def run_validation(repos):
    print("=" * 60)
    print("VALIDAÇÃO COM AMOSTRA")
    print("=" * 60)
    validate_rq01(repos, VALIDATION_SAMPLE_SIZE)
    print()
    validate_rq02(repos, VALIDATION_SAMPLE_SIZE)
    print()
    validate_rq03(repos, VALIDATION_SAMPLE_SIZE)
    print()
    validate_rq04(repos, VALIDATION_SAMPLE_SIZE)
    print()
    validate_rq05(repos, VALIDATION_SAMPLE_SIZE)
    print()
    validate_rq06(repos, VALIDATION_SAMPLE_SIZE)
    print()

def run_full_analysis(repos):
    print("=" * 60)
    print("ANÁLISE COMPLETA")
    print("=" * 60)

    rq01 = process_rq01(repos)
    print(f"\nRQ01 - Idade dos repositórios:")
    print(f"  Mediana: {rq01['median_age_years']} anos")
    print(f"  Média: {rq01['mean_age_years']} anos")
    print(f"  Min: {rq01['min_age']} | Max: {rq01['max_age']}")
    save_csv("rq01_age.csv", rq01["results"], ["repository", "created_at", "age_years", "stars"])

    rq02 = process_rq02(repos)
    print(f"\nRQ02 - Pull Requests aceitas:")
    print(f"  Mediana: {rq02['median_merged_prs']}")
    print(f"  Média: {rq02['mean_merged_prs']}")
    print(f"  Min: {rq02['min_prs']} | Max: {rq02['max_prs']}")
    save_csv("rq02_pull_requests.csv", rq02["results"], ["repository", "merged_prs", "stars"])

    rq03 = process_rq03(repos)
    print(f"\nRQ03 - Total de releases:")
    print(f"  Mediana: {rq03['median_releases']}")
    print(f"  Média: {rq03['mean_releases']}")
    print(f"  Min: {rq03['min_releases']} | Max: {rq03['max_releases']}")
    save_csv("rq03_releases.csv", rq03["results"], ["repository", "total_releases", "stars"])

    rq04 = process_rq04(repos)
    print(f"\nRQ04 - Tempo até última atualização:")
    print(f"  Mediana: {rq04['median_days_since_update']} dias")
    print(f"  Média: {rq04['mean_days_since_update']} dias")
    print(f"  Min: {rq04['min_days']} | Max: {rq04['max_days']}")
    save_csv("rq04_update_frequency.csv", rq04["results"], ["repository", "updated_at", "days_since_update", "stars"])

    rq05 = process_rq05(repos)
    print(f"\nRQ05 - Linguagens primárias:")
    for lang, count in rq05["top_languages"]:
        is_popular = "POPULAR" if lang in POPULAR_LANGUAGES_TIOBE else "não-popular"
        print(f"  {lang}: {count} repositórios ({is_popular})")
    save_csv("rq05_languages.csv", rq05["results"], ["repository", "primary_language", "stars"])

    rq06 = process_rq06(repos)
    print(f"\nRQ06 - Razão de issues fechadas:")
    print(f"  Mediana: {rq06['median_closed_ratio']}")
    print(f"  Média: {rq06['mean_closed_ratio']}")
    print(f"  Min: {rq06['min_ratio']} | Max: {rq06['max_ratio']}")
    save_csv("rq06_issues.csv", rq06["results"], ["repository", "total_issues", "closed_issues", "closed_ratio", "stars"])

    summary = {
        "total_repos": len(repos),
        "rq01_median_age_years": rq01["median_age_years"],
        "rq02_median_merged_prs": rq02["median_merged_prs"],
        "rq03_median_releases": rq03["median_releases"],
        "rq04_median_days_since_update": rq04["median_days_since_update"],
        "rq05_top_languages": rq05["top_languages"],
        "rq06_median_closed_ratio": rq06["median_closed_ratio"]
    }
    with open(os.path.join(DATA_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResumo salvo em {DATA_DIR}/summary.json")

if __name__ == "__main__":
    repos = fetch_repos()
    run_validation(repos)
    run_full_analysis(repos)