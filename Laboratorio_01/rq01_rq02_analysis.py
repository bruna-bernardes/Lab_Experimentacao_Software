import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_client import fetch_repos
from rq01_age import process_rq01, validate_rq01
from rq02_pull_requests import process_rq02, validate_rq02
from config import NUM_REPOS, VALIDATION_SAMPLE_SIZE

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

if __name__ == "__main__":
    repos = fetch_repos()
    
    print("=" * 60)
    print("PESSOA A — RQ01 (Idade) + RQ02 (Pull Requests)")
    print("=" * 60)
    
    print("\n--- Validação RQ01 ---")
    validate_rq01(repos, VALIDATION_SAMPLE_SIZE)
    
    print("\n--- Validação RQ02 ---")
    validate_rq02(repos, VALIDATION_SAMPLE_SIZE)
    
    rq01 = process_rq01(repos)
    rq02 = process_rq02(repos)
    
    print(f"\nRQ01 - Idade mediana: {rq01['median_age_years']} anos")
    print(f"RQ02 - PRs aceitas (mediana): {rq02['median_merged_prs']}")
    
    import csv
    with open(os.path.join(DATA_DIR, "rq01_age.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["repository", "created_at", "age_years", "stars"])
        writer.writeheader()
        writer.writerows(rq01["results"])
    
    with open(os.path.join(DATA_DIR, "rq02_pull_requests.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["repository", "merged_prs", "stars"])
        writer.writeheader()
        writer.writerows(rq02["results"])
    
    print("\nCSVs salvos em data/rq01_age.csv e data/rq02_pull_requests.csv")