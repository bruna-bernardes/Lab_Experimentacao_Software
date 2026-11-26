"""Executa uma janela da coleta confirmatória da Sprint 2.

Responsável: Bruna Bernardes (instrumentação e operação).

Uso, a partir desta pasta:

    python3 coleta_s02.py --janela noite
    python3 coleta_s02.py --janela dia
    python3 validar_s02.py

Se o CSV da janela já existe, o comando para. A janela congelada não é refeita.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from medicao import executar_coleta, ler_urls

JANELAS = ("noite", "dia")


def caminhos_s02(janela: str, base: Path | None = None) -> dict[str, Path]:
    if janela not in JANELAS:
        raise ValueError("janela deve ser noite ou dia")
    pasta = base or Path(__file__).resolve().parent
    dados = pasta / "dados"
    return {
        "urls": pasta / "urls_s02.csv",
        "csv": dados / f"coleta_s02_{janela}.csv",
        "robots": dados / f"robots_s02_{janela}.txt",
        "meta": dados / f"coleta_s02_{janela}_meta.json",
        "validacao": dados / f"validacao_s02_{janela}.json",
    }


def nota_da_janela(janela: str) -> str:
    return (
        f"Coleta confirmatória da Sprint 2, janela {janela}. "
        "Não substitui o piloto da Sprint 1."
    )


def janela_congelada(janela: str, base: Path | None = None) -> bool:
    return caminhos_s02(janela, base)["csv"].exists()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--janela", required=True, choices=JANELAS)
    args = parser.parse_args(argv)
    caminhos = caminhos_s02(args.janela)
    if janela_congelada(args.janela):
        print(f"já existe {caminhos['csv'].name}; a janela não foi refeita")
        return 2
    urls = ler_urls(caminhos["urls"])
    print(f"coletando {len(urls)} páginas × 3 repetições, janela {args.janela}, no máximo 1 requisição/s")
    executar_coleta(
        urls,
        destino_csv=caminhos["csv"],
        destino_robots=caminhos["robots"],
        destino_meta=caminhos["meta"],
        nota=nota_da_janela(args.janela),
    )
    print(f"CSV: {caminhos['csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
