import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_client import fetch_repos
from rq05_languages import process_rq05, validate_rq05
from rq06_issues import process_rq06, validate_rq06
from config import NUM_REPOS, VALIDATION_SAMPLE_SIZE

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

if __name__ == "__main__":
    repos = fetch_repos()
    
    print("=" * 60)
    print("PESSOA C — RQ05 (Linguagens) + RQ06 (Issues Fechadas)")
    print("=" * 60)
    
    print("\n--- Validação RQ05 ---")
    validate_rq05(repos, VALIDATION_SAMPLE_SIZE)
    
    print("\n--- Validação RQ06 ---")
    validate_rq06(repos, VALIDATION_SAMPLE_SIZE)
    
    rq05 = process_rq05(repos)
    rq06 = process_rq06(repos)
    
    print(f"\nRQ05 - Top 5 linguagens: {rq05['top_languages'][:5]}")
    print(f"RQ06 - Razão issues fechadas (mediana): {rq06['median_closed_ratio']}")
    
    import csv
    with open(os.path.join(DATA_DIR, "rq05_languages.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["repository", "primary_language", "stars"])
        writer.writeheader()
        writer.writerows(rq05["results"])
    
    with open(os.path.join(DATA_DIR, "rq06_issues.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["repository", "total_issues", "closed_issues", "closed_ratio", "stars"])
        writer.writeheader()
        writer.writerows(rq06["results"])
    
    print("\nCSVs salvos em data/rq05_languages.csv e data/rq06_issues.csv")