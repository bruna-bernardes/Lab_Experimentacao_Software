"""Executa a coleta piloto da Sprint 1.

Responsável: Bruna Bernardes (instrumentação e operação).

Uso, a partir desta pasta:

    python3 coleta_piloto.py
    python3 validar_piloto.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from medicao import caminhos_padrao, executar_coleta, ler_urls


def main() -> int:
    caminhos = caminhos_padrao()
    urls = ler_urls(caminhos["urls"])
    print(f"coletando {len(urls)} páginas × 3 repetições, no máximo 1 requisição/s")
    executar_coleta(
        urls,
        destino_csv=caminhos["csv"],
        destino_robots=caminhos["robots"],
        destino_meta=caminhos["meta"],
    )
    print(f"CSV: {caminhos['csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
