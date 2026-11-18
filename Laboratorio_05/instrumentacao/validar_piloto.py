"""Validação da coleta piloto.

Responsável: Bruna Bernardes (instrumentação e operação).

Confere o contrato do CSV antes de qualquer análise: completude, tipos,
coerência da rubrica de segurança, host final e o intervalo entre
requisições.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from medicao import COLUNAS, HOST_ALVO, ITENS_CONJUNTO_MINIMO, ITENS_PONTUACAO, caminhos_padrao, ler_urls

INTERVALO_MINIMO_ACEITO_S = 0.95


def _ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if tuple(leitor.fieldnames or ()) != COLUNAS:
            raise ValueError("colunas do CSV diferem do contrato de medicao.COLUNAS")
        return list(leitor)


def _inteiro(linha: dict[str, str], coluna: str) -> int:
    return int(linha[coluna])


def _flutuante(linha: dict[str, str], coluna: str) -> float:
    return float(linha[coluna])


def problemas(linhas: list[dict[str, str]], urls: list[dict[str, str]], texto_robots: str) -> list[str]:
    achados = []
    if "user-agent" not in texto_robots.lower():
        achados.append("robots.txt ausente ou sem regras User-agent")
    esperadas = {(url["id_pagina"], repeticao) for url in urls for repeticao in (1, 2, 3)}
    vistas = set()
    momentos = []
    for indice, linha in enumerate(linhas, start=2):
        chave = (linha["id_pagina"], int(linha["repeticao"]) if linha["repeticao"].isdigit() else -1)
        if chave in vistas:
            achados.append(f"linha {indice}: repetição duplicada {chave}")
        vistas.add(chave)
        if linha["erro"]:
            achados.append(f"linha {indice}: erro de coleta ({linha['erro']})")
            continue
        if linha["grupo"] not in {"portal", "orgao"}:
            achados.append(f"linha {indice}: grupo inválido")
        if linha["status_http"] != "200":
            achados.append(f"linha {indice}: status {linha['status_http']}")
        host = urlsplit(linha["url_final"]).hostname
        if host != HOST_ALVO:
            achados.append(f"linha {indice}: url_final fora de {HOST_ALVO} ({linha['url_final']})")
        try:
            tls = _flutuante(linha, "tempo_tls_ms")
            ttfb = _flutuante(linha, "ttfb_ms")
            total = _flutuante(linha, "tempo_total_ms")
            if not (0 <= tls <= ttfb <= total):
                achados.append(f"linha {indice}: tempos fora de ordem ({tls}, {ttfb}, {total})")
            if _inteiro(linha, "bytes_transferidos") <= 0 or _inteiro(linha, "bytes_html") <= 0:
                achados.append(f"linha {indice}: tamanho não positivo")
            flags = {item: _inteiro(linha, item) for item in ITENS_PONTUACAO}
        except ValueError:
            achados.append(f"linha {indice}: número inválido")
            continue
        if any(valor not in (0, 1) for valor in flags.values()):
            achados.append(f"linha {indice}: indicador fora de 0/1")
        if _inteiro(linha, "pontuacao_seguranca") != sum(flags.values()):
            achados.append(f"linha {indice}: pontuação não fecha com os indicadores")
        minimo = int(all(flags[item] == 1 for item in ITENS_CONJUNTO_MINIMO))
        if _inteiro(linha, "atende_conjunto_minimo") != minimo:
            achados.append(f"linha {indice}: conjunto mínimo incoerente com os indicadores")
        try:
            momentos.append(datetime.fromisoformat(linha["coletado_em_utc"]))
        except ValueError:
            achados.append(f"linha {indice}: data inválida")
    if vistas != esperadas:
        faltam = esperadas - vistas
        sobram = vistas - esperadas
        if faltam:
            achados.append(f"faltam medições: {sorted(faltam)[:5]}")
        if sobram:
            achados.append(f"medições inesperadas: {sorted(sobram)[:5]}")
    for anterior, atual in zip(momentos, momentos[1:]):
        delta = (atual - anterior).total_seconds()
        if delta < INTERVALO_MINIMO_ACEITO_S:
            achados.append(f"intervalo de {delta:.3f}s entre requisições; o mínimo aceito é {INTERVALO_MINIMO_ACEITO_S}s")
            break
    return achados


def validar(caminhos: dict[str, Path] | None = None) -> dict:
    caminhos = caminhos or caminhos_padrao()
    urls = ler_urls(caminhos["urls"])
    linhas = _ler_csv(caminhos["csv"])
    texto_robots = caminhos["robots"].read_text(encoding="utf-8") if caminhos["robots"].exists() else ""
    achados = problemas(linhas, urls, texto_robots)
    relatorio = {
        "valido": not achados,
        "linhas": len(linhas),
        "paginas_planejadas": len(urls),
        "problemas": achados,
    }
    caminhos["validacao"].parent.mkdir(parents=True, exist_ok=True)
    caminhos["validacao"].write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return relatorio


def main() -> int:
    relatorio = validar()
    if relatorio["valido"]:
        print(f"piloto válido: {relatorio['linhas']} linhas")
        return 0
    print(f"piloto inválido ({len(relatorio['problemas'])} problemas)")
    for achado in relatorio["problemas"]:
        print(f"- {achado}")
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
