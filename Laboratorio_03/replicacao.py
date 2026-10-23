"""Prepara e compara uma replicação sobre 30 repositórios.

Uso para preparar a amostra:
    python replicacao.py --preparar

Uso após executar o pipeline replicador e salvar o CSV comparável:
    python replicacao.py --comparar caminho/resultado_replicado.csv
"""
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
DATASET = ROOT / "resultados" / "dataset_final.csv"
OUT = ROOT / "resultados" / "replicacao"
METRICS = ["deployment_frequency_semana", "lead_time_release_horas",
           "lead_time_commit_horas", "cfr_ci", "cfr_entrega", "recuperacao_horas"]


def preparar():
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(DATASET)
    amostra = df.sample(n=min(30, len(df)), random_state=42).sort_values("repositorio")
    amostra.to_csv(OUT / "amostra_30.csv", index=False)
    print(f"Amostra preparada em {OUT / 'amostra_30.csv'}")


def comparar(caminho):
    original = pd.read_csv(OUT / "amostra_30.csv")
    replicado = pd.read_csv(caminho)
    if "repositorio" not in replicado:
        raise ValueError("O CSV replicado precisa conter a coluna repositorio.")
    merged = original.merge(replicado, on="repositorio", suffixes=("_original", "_replicado"))
    linhas = []
    for metric in METRICS:
        a = pd.to_numeric(merged[f"{metric}_original"], errors="coerce")
        b = pd.to_numeric(merged[f"{metric}_replicado"], errors="coerce")
        valid = a.notna() & b.notna()
        diff = ((b[valid] - a[valid]).abs() / a[valid].abs().replace(0, pd.NA)).dropna()
        linhas.append({"metrica": metric, "n": int(valid.sum()),
                       "mediana_original": a[valid].median(),
                       "mediana_replicado": b[valid].median(),
                       "diferenca_relativa_mediana": diff.median() if len(diff) else pd.NA})
    resultado = pd.DataFrame(linhas)
    OUT.mkdir(exist_ok=True)
    resultado.to_csv(OUT / "comparacao_metricas.csv", index=False)
    merged.to_csv(OUT / "comparacao_repositorios.csv", index=False)
    print(f"Comparação gravada em {OUT}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preparar", action="store_true")
    parser.add_argument("--comparar")
    args = parser.parse_args()
    if args.preparar:
        preparar()
    elif args.comparar:
        comparar(args.comparar)
    else:
        parser.error("use --preparar ou --comparar CSV")


if __name__ == "__main__":
    main()
