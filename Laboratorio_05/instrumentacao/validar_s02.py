"""Validação das duas janelas da Sprint 2.

Responsável: Bruna Bernardes (instrumentação e operação).

Cada janela usa o mesmo contrato do piloto. A janela que ainda não foi
coletada não reprova a que já está no disco: o comando só fecha quando
as duas existem e passam.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coleta_s02 import JANELAS, caminhos_s02
from medicao import ler_urls
from validar_piloto import _ler_csv, problemas


def validar_janela(janela: str, base: Path | None = None) -> dict:
    caminhos = caminhos_s02(janela, base)
    if not caminhos["csv"].exists():
        return {"janela": janela, "presente": False, "valido": False, "problemas": ["csv ausente"]}
    urls = ler_urls(caminhos["urls"])
    linhas = _ler_csv(caminhos["csv"])
    texto_robots = caminhos["robots"].read_text(encoding="utf-8") if caminhos["robots"].exists() else ""
    achados = problemas(linhas, urls, texto_robots)
    relatorio = {
        "janela": janela,
        "presente": True,
        "valido": not achados,
        "linhas": len(linhas),
        "paginas_planejadas": len(urls),
        "problemas": achados,
    }
    caminhos["validacao"].parent.mkdir(parents=True, exist_ok=True)
    caminhos["validacao"].write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return relatorio


def main() -> int:
    relatorios = [validar_janela(janela) for janela in JANELAS]
    for relatorio in relatorios:
        if not relatorio["presente"]:
            print(f"{relatorio['janela']}: ainda não coletada")
            continue
        if relatorio["valido"]:
            print(f"{relatorio['janela']}: válida, {relatorio['linhas']} linhas")
        else:
            print(f"{relatorio['janela']}: inválida ({len(relatorio['problemas'])} problemas)")
            for achado in relatorio["problemas"]:
                print(f"- {achado}")
    if any(relatorio["presente"] and not relatorio["valido"] for relatorio in relatorios):
        return 1
    if any(not relatorio["presente"] for relatorio in relatorios):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
