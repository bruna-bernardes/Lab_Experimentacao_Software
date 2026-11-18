"""Medição educada do portal GOV.BR.

Responsável: Bruna Bernardes (instrumentação e operação).

O módulo baixa HTML público como um cliente anônimo, com no máximo uma
requisição HTTP por segundo. Não autentica, não grava o corpo da página
e não grava cookies.
"""

from __future__ import annotations

import csv
import gzip
import http.client
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urljoin

USER_AGENT = (
    "LabExperimentacaoSoftware-PUCMinas/1.0 "
    "(+https://github.com/bruna-bernardes/Lab_Experimentacao_Software; "
    "estudo academico; sem dados pessoais)"
)
HOST_ALVO = "www.gov.br"
INTERVALO_MINIMO_S = 1.0
TIMEOUT_S = 20
LIMITE_BYTES = 5_000_000
REPETICOES_PILOTO = 3

ITENS_CONJUNTO_MINIMO = (
    "hsts",
    "nosniff",
    "clickjacking",
    "referrer_policy",
    "csp",
)
ITENS_PONTUACAO = ITENS_CONJUNTO_MINIMO + (
    "hsts_include_subdomains",
    "csp_alem_de_frame",
    "permissions_policy",
)

COLUNAS = (
    "id_pagina",
    "grupo",
    "rotulo",
    "url_solicitada",
    "url_final",
    "repeticao",
    "coletado_em_utc",
    "status_http",
    "redirecionamentos",
    "tempo_tls_ms",
    "ttfb_ms",
    "tempo_total_ms",
    "bytes_transferidos",
    "bytes_html",
    "content_encoding",
    "cache",
    "servidor",
    "hsts",
    "hsts_include_subdomains",
    "nosniff",
    "clickjacking",
    "referrer_policy",
    "csp",
    "csp_alem_de_frame",
    "permissions_policy",
    "pontuacao_seguranca",
    "atende_conjunto_minimo",
    "valor_hsts",
    "valor_csp",
    "valor_x_frame_options",
    "valor_referrer_policy",
    "valor_x_content_type_options",
    "valor_permissions_policy",
    "erro",
)

CABECALHOS_PEDIDO = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Encoding": "gzip",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Connection": "close",
}


class Limitador:
    """Garante um intervalo mínimo entre o início de requisições seguidas."""

    def __init__(self, intervalo: float = INTERVALO_MINIMO_S, relogio=time.monotonic, dormir=time.sleep):
        if intervalo <= 0:
            raise ValueError("o intervalo precisa ser positivo")
        self.intervalo = intervalo
        self.relogio = relogio
        self.dormir = dormir
        self._proxima = None
        self.esperas = 0

    def aguardar(self) -> None:
        while self._proxima is not None and self.relogio() < self._proxima:
            self.dormir(self._proxima - self.relogio())
            self.esperas += 1
        self._proxima = self.relogio() + self.intervalo


def regras_disallow_agente_estrela(texto: str) -> list[str]:
    """Reúne as regras Disallow dos grupos User-agent: *."""
    grupos: list[dict] = []
    atual = None
    for bruto in texto.splitlines():
        linha = bruto.split("#", 1)[0].strip()
        if not linha or ":" not in linha:
            continue
        chave, valor = linha.split(":", 1)
        chave = chave.strip().lower()
        valor = valor.strip()
        if chave == "user-agent":
            if atual is None or atual["tem_regra"]:
                atual = {"agentes": [], "disallow": [], "tem_regra": False}
                grupos.append(atual)
            atual["agentes"].append(valor.lower())
        elif atual is not None and chave == "disallow":
            atual["tem_regra"] = True
            if valor:
                atual["disallow"].append(valor)
        elif atual is not None and chave == "allow":
            atual["tem_regra"] = True
    regras: list[str] = []
    for grupo in grupos:
        if "*" in grupo["agentes"]:
            regras.extend(grupo["disallow"])
    return regras


def regra_casa(regra: str, caminho: str) -> bool:
    """Aplica uma regra no estilo do robots.txt (* e $) ao caminho."""
    ancora_fim = regra.endswith("$")
    corpo = regra[:-1] if ancora_fim else regra
    partes = [".*" if caractere == "*" else re.escape(caractere) for caractere in corpo]
    expressao = "^" + "".join(partes)
    if ancora_fim:
        expressao += "$"
    return re.search(expressao, caminho) is not None


def caminho_bloqueado(texto_robots: str, caminho: str) -> bool:
    return any(regra_casa(regra, caminho) for regra in regras_disallow_agente_estrela(texto_robots))


def caminho_da_url(url: str) -> str:
    partes = urlsplit(url)
    caminho = partes.path or "/"
    if partes.query:
        return f"{caminho}?{partes.query}"
    return caminho


def _max_age_positivo(valor: str) -> bool:
    encontrado = re.search(r"max-age\s*=\s*(\d+)", valor.lower())
    return bool(encontrado) and int(encontrado.group(1)) > 0


def classe_cache(cabecalhos: dict[str, str]) -> str:
    for nome in ("x-cache-f", "x-cache", "x-cache-b"):
        valor = cabecalhos.get(nome, "").upper()
        if "HIT" in valor:
            return "HIT"
        if "MISS" in valor:
            return "MISS"
        if valor.strip():
            return "OUTRO"
    return "AUSENTE"


def avaliar_cabecalhos(cabecalhos: dict[str, str]) -> dict[str, int | str]:
    """Traduz cabeçalhos HTTP na rubrica de segurança do estudo."""
    normalizados = {str(chave).lower(): str(valor) for chave, valor in cabecalhos.items()}
    hsts_valor = normalizados.get("strict-transport-security", "")
    csp_valor = normalizados.get("content-security-policy", "")
    xfo_valor = normalizados.get("x-frame-options", "")
    referrer_valor = normalizados.get("referrer-policy", "")
    xcto_valor = normalizados.get("x-content-type-options", "")
    permissions_valor = normalizados.get("permissions-policy", "")
    csp_minusculo = csp_valor.lower()
    xfo_minusculo = xfo_valor.lower()

    indicadores = {
        "hsts": int(bool(hsts_valor) and _max_age_positivo(hsts_valor)),
        "hsts_include_subdomains": int("includesubdomains" in hsts_valor.lower()),
        "nosniff": int("nosniff" in xcto_valor.lower()),
        "clickjacking": int(
            "deny" in xfo_minusculo or "sameorigin" in xfo_minusculo or "frame-ancestors" in csp_minusculo
        ),
        "referrer_policy": int(bool(referrer_valor.strip())),
        "csp": int(bool(csp_valor.strip())),
        "csp_alem_de_frame": int("default-src" in csp_minusculo or "script-src" in csp_minusculo),
        "permissions_policy": int(bool(permissions_valor.strip())),
    }
    pontuacao = sum(indicadores[item] for item in ITENS_PONTUACAO)
    atende = int(all(indicadores[item] == 1 for item in ITENS_CONJUNTO_MINIMO))
    return {
        **indicadores,
        "pontuacao_seguranca": pontuacao,
        "atende_conjunto_minimo": atende,
        "cache": classe_cache(normalizados),
        "servidor": normalizados.get("server", "")[:180],
        "valor_hsts": hsts_valor[:300],
        "valor_csp": csp_valor[:500],
        "valor_x_frame_options": xfo_valor[:200],
        "valor_referrer_policy": referrer_valor[:200],
        "valor_x_content_type_options": xcto_valor[:200],
        "valor_permissions_policy": permissions_valor[:300],
    }


def _cabecalhos_da_resposta(resposta: http.client.HTTPResponse) -> dict[str, str]:
    return {chave.lower(): valor for chave, valor in resposta.getheaders()}


def um_salto(url: str, timeout: float = TIMEOUT_S) -> dict:
    """Faz um GET HTTPS e mede TLS, primeiro byte e leitura do corpo."""
    partes = urlsplit(url)
    if partes.scheme != "https" or not partes.hostname:
        raise ValueError(f"somente https com host: {url}")
    caminho = caminho_da_url(url)
    conexao = http.client.HTTPSConnection(partes.hostname, partes.port or 443, timeout=timeout)
    try:
        inicio = time.perf_counter()
        conexao.connect()
        depois_tls = time.perf_counter()
        conexao.request("GET", caminho, headers=CABECALHOS_PEDIDO)
        resposta = conexao.getresponse()
        primeiro_byte = time.perf_counter()
        bruto = resposta.read(LIMITE_BYTES + 1)
        fim = time.perf_counter()
        if len(bruto) > LIMITE_BYTES:
            raise RuntimeError("resposta acima do limite de 5 MB")
        codificacao = (resposta.getheader("Content-Encoding") or "").lower()
        decodificado = decodificar_corpo(bruto, codificacao)
        bytes_html = len(decodificado)
        content_encoding = codificacao or "identity"
        return {
            "status": resposta.status,
            "location": resposta.getheader("Location"),
            "tempo_tls_ms": (depois_tls - inicio) * 1000,
            "ttfb_ms": (primeiro_byte - inicio) * 1000,
            "tempo_total_ms": (fim - inicio) * 1000,
            "bytes_transferidos": len(bruto),
            "bytes_html": bytes_html,
            "content_encoding": content_encoding,
            "cabecalhos": _cabecalhos_da_resposta(resposta),
        }
    finally:
        conexao.close()


def baixar(url: str, limitador: Limitador, timeout: float = TIMEOUT_S, max_saltos: int = 5) -> dict:
    """Segue redirecionamentos. O tempo medido não inclui a espera do limitador."""
    atual = url
    vistos = set()
    tempo_tls = ttfb = total = 0.0
    redirecionamentos = 0
    coletado_em = None
    for _ in range(max_saltos + 1):
        if atual in vistos:
            raise RuntimeError("redirecionamento em ciclo")
        vistos.add(atual)
        limitador.aguardar()
        if coletado_em is None:
            coletado_em = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        salto = um_salto(atual, timeout=timeout)
        tempo_tls += salto["tempo_tls_ms"]
        total += salto["tempo_total_ms"]
        if salto["status"] in (301, 302, 303, 307, 308) and salto["location"]:
            redirecionamentos += 1
            ttfb += salto["tempo_total_ms"]
            atual = urljoin(atual, salto["location"])
            continue
        ttfb += salto["ttfb_ms"]
        avaliacao = avaliar_cabecalhos(salto["cabecalhos"])
        return {
            "url_final": atual,
            "status_http": salto["status"],
            "redirecionamentos": redirecionamentos,
            "tempo_tls_ms": tempo_tls,
            "ttfb_ms": ttfb,
            "tempo_total_ms": total,
            "bytes_transferidos": salto["bytes_transferidos"],
            "bytes_html": salto["bytes_html"],
            "content_encoding": salto["content_encoding"],
            **avaliacao,
            "coletado_em_utc": coletado_em,
            "erro": "",
        }
    raise RuntimeError("limite de redirecionamentos excedido")


def decodificar_corpo(corpo: bytes, content_encoding: str) -> bytes:
    if content_encoding.lower() == "gzip":
        return gzip.decompress(corpo)
    return corpo


def obter_robots(limitador: Limitador, timeout: float = TIMEOUT_S) -> tuple[int, str]:
    limitador.aguardar()
    conexao = http.client.HTTPSConnection(HOST_ALVO, 443, timeout=timeout)
    try:
        conexao.request("GET", "/robots.txt", headers=CABECALHOS_PEDIDO)
        resposta = conexao.getresponse()
        corpo = resposta.read(LIMITE_BYTES + 1)
        if len(corpo) > LIMITE_BYTES:
            raise RuntimeError("robots.txt acima do limite")
        codificacao = resposta.getheader("Content-Encoding") or ""
        corpo = decodificar_corpo(corpo, codificacao)
        return resposta.status, corpo.decode("utf-8", errors="replace")
    finally:
        conexao.close()


def ler_urls(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if not linhas:
        raise ValueError(f"lista de URLs vazia: {caminho}")
    for linha in linhas:
        if set(linha) < {"id_pagina", "grupo", "rotulo", "url"}:
            raise ValueError("urls_piloto.csv precisa das colunas id_pagina, grupo, rotulo e url")
        if urlsplit(linha["url"]).hostname != HOST_ALVO:
            raise ValueError(f"URL fora de {HOST_ALVO}: {linha['url']}")
    return linhas


def _numero(valor: float) -> str:
    return f"{valor:.3f}"


def linha_de_medicao(pagina: dict[str, str], repeticao: int, medido: dict) -> dict[str, str]:
    linha = {coluna: "" for coluna in COLUNAS}
    linha.update(
        {
            "id_pagina": pagina["id_pagina"],
            "grupo": pagina["grupo"],
            "rotulo": pagina["rotulo"],
            "url_solicitada": pagina["url"],
            "url_final": medido.get("url_final", ""),
            "repeticao": str(repeticao),
            "coletado_em_utc": medido.get("coletado_em_utc")
            or datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "status_http": "" if medido.get("status_http") is None else str(medido.get("status_http")),
            "redirecionamentos": "" if medido.get("redirecionamentos") is None else str(medido.get("redirecionamentos")),
            "content_encoding": medido.get("content_encoding", ""),
            "cache": medido.get("cache", ""),
            "servidor": medido.get("servidor", ""),
            "erro": medido.get("erro", ""),
        }
    )
    for coluna in (
        "tempo_tls_ms",
        "ttfb_ms",
        "tempo_total_ms",
    ):
        if medido.get(coluna) is not None:
            linha[coluna] = _numero(float(medido[coluna]))
    for coluna in ("bytes_transferidos", "bytes_html", "pontuacao_seguranca", "atende_conjunto_minimo", *ITENS_PONTUACAO):
        if medido.get(coluna) is not None and medido.get(coluna) != "":
            linha[coluna] = str(int(medido[coluna]))
    for coluna in (
        "valor_hsts",
        "valor_csp",
        "valor_x_frame_options",
        "valor_referrer_policy",
        "valor_x_content_type_options",
        "valor_permissions_policy",
    ):
        linha[coluna] = str(medido.get(coluna, ""))
    return linha


def escrever_csv(caminho: Path, linhas: list[dict[str, str]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)


def executar_coleta(
    urls: list[dict[str, str]],
    destino_csv: Path,
    destino_robots: Path,
    destino_meta: Path,
    repeticoes: int = REPETICOES_PILOTO,
    limitador: Limitador | None = None,
    obter_robots_fn=obter_robots,
    baixar_fn=baixar,
    mostrar=print,
) -> dict:
    """Coleta em rodadas: cada repetição percorre todas as páginas uma vez."""
    limitador = limitador or Limitador()
    status_robots, texto_robots = obter_robots_fn(limitador)
    if status_robots != 200 or "user-agent" not in texto_robots.lower():
        raise RuntimeError(f"robots.txt indisponível (status {status_robots}); coleta interrompida")
    bloqueadas = [
        pagina["url"]
        for pagina in urls
        if caminho_bloqueado(texto_robots, caminho_da_url(pagina["url"]))
    ]
    if bloqueadas:
        raise RuntimeError("robots.txt desautoriza: " + ", ".join(bloqueadas))

    destino_robots.parent.mkdir(parents=True, exist_ok=True)
    destino_robots.write_text(texto_robots, encoding="utf-8")
    inicio = datetime.now(timezone.utc)
    linhas = []
    for repeticao in range(1, repeticoes + 1):
        for pagina in urls:
            try:
                medido = baixar_fn(pagina["url"], limitador)
            except Exception as erro:  # noqa: BLE001 — uma página ruim não pode derrubar o piloto
                medido = {"erro": str(erro)[:300], "url_final": "", "status_http": None}
            linhas.append(linha_de_medicao(pagina, repeticao, medido))
            mostrar(
                f"{len(linhas):02d}/{len(urls) * repeticoes} "
                f"{pagina['id_pagina']} rep {repeticao} "
                f"status={linhas[-1]['status_http'] or 'erro'} "
                f"total={linhas[-1]['tempo_total_ms'] or '-'} ms"
            )
    escrever_csv(destino_csv, linhas)
    fim = datetime.now(timezone.utc)
    meta = {
        "software": "Portal GOV.BR",
        "host": HOST_ALVO,
        "iniciado_em_utc": inicio.isoformat(timespec="seconds"),
        "finalizado_em_utc": fim.isoformat(timespec="seconds"),
        "intervalo_minimo_s": limitador.intervalo,
        "repeticoes": repeticoes,
        "paginas": len(urls),
        "user_agent": USER_AGENT,
        "robots_status": status_robots,
        "requisicoes_http_previstas": 1 + len(urls) * repeticoes,
        "nota": "Coleta piloto da Sprint 1. A amostra confirmatória fica para a Sprint 2.",
    }
    destino_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def caminhos_padrao(base: Path | None = None) -> dict[str, Path]:
    pasta = base or Path(__file__).resolve().parent
    dados = pasta / "dados"
    return {
        "urls": pasta / "urls_piloto.csv",
        "csv": dados / "piloto_s01.csv",
        "robots": dados / "robots_www.gov.br.txt",
        "meta": dados / "piloto_s01_meta.json",
        "validacao": dados / "validacao_piloto.json",
    }
