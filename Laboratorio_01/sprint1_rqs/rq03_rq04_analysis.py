import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Laboratorio_01.códigos.api_client import fetch_repos
from Laboratorio_01.sprint1_rqs.rq03_releases import process_rq03, validate_rq03
from Laboratorio_01.sprint1_rqs.rq04_update_frequency import process_rq04, validate_rq04
from Laboratorio_01.códigos.config import NUM_REPOS, VALIDATION_SAMPLE_SIZE

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

if __name__ == "__main__":
    repos = fetch_repos()
    
    print("=" * 60)
    print("PESSOA B — RQ03 (Releases) + RQ04 (Frequência de Atualização)")
    print("=" * 60)
    
    print("\n--- Validação RQ03 ---")
    validate_rq03(repos, VALIDATION_SAMPLE_SIZE)
    
    print("\n--- Validação RQ04 ---")
    validate_rq04(repos, VALIDATION_SAMPLE_SIZE)
    
    rq03 = process_rq03(repos)
    rq04 = process_rq04(repos)
    
    print(f"\nRQ03 - Releases (mediana): {rq03['median_releases']}")
    print(f"RQ04 - Dias desde última atualização (mediana): {rq04['median_days_since_update']}")
    
    import csv
    with open(os.path.join(DATA_DIR, "rq03_releases.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["repository", "total_releases", "stars"])
        writer.writeheader()
        writer.writerows(rq03["results"])
    
    with open(os.path.join(DATA_DIR, "rq04_update_frequency.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["repository", "updated_at", "days_since_update", "stars"])
        writer.writeheader()
        writer.writerows(rq04["results"])
    
    print("\nCSVs salvos em data/rq03_releases.csv e data/rq04_update_frequency.csv")