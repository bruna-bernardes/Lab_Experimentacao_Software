"""Seleção de repositórios candidatos e coleta de metadados.

Sprint 2 (Lab03S02):
- O pool de candidatos passa a ser a população completa retornada pela busca
  (todas as faixas de estrelas), embaralhada com semente fixa. Na Sprint 1 as
  faixas eram percorridas em ordem e a amostra ficou concentrada em
  1.001–1.025 estrelas.
- A busca usa ``sort=stars`` (ordem estável entre dias; ``updated`` muda sempre).
- Contribuidores são contados pelo cabeçalho ``Link`` (``per_page=1``), sem
  baixar a lista inteira.
- A idade do repositório é calculada em relação ao fim da janela, e não ao dia
  da execução, para que o valor seja reprodutível.
"""
import random
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import requests
from requests.exceptions import HTTPError

FAIXAS_PADRAO = [
    (1001, 2000),
    (2001, 5000),
    (5001, 10000),
    (10001, 1000000)
]

FILTRO_BUSCA = "archived:false fork:false"


def converter_data(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def buscar_faixa(api, minimo, maximo):
    """Retorna os repositórios da faixa de estrelas, dividindo-a enquanto a
    busca indicar mais de 1.000 resultados (limite da Search API)."""
    parametros = {
        "q": f"stars:{minimo}..{maximo} {FILTRO_BUSCA}",
        "sort": "stars",
        "order": "desc",
        "per_page": 100
    }

    resposta = api.get("/search/repositories", parametros)
    total = resposta["data"].get("total_count", 0)

    if total > 1000 and minimo < maximo:
        meio = (minimo + maximo) // 2
        yield from buscar_faixa(api, minimo, meio)
        yield from buscar_faixa(api, meio + 1, maximo)
        return

    if total > 1000:
        print(f"Aviso: {total} repositórios com {minimo} estrelas; "
              "apenas os 1.000 primeiros são acessíveis pela busca.")

    yield from api.paginas("/search/repositories", parametros, limite=1000)


def montar_pool(api, faixas=None):
    """Lista deduplicada de candidatos (nome e estrelas) de todas as faixas,
    ordenada por nome para não depender da ordem devolvida pela API."""
    pool = {}

    for minimo, maximo in faixas or FAIXAS_PADRAO:
        for repo in buscar_faixa(api, minimo, maximo):
            nome = repo["full_name"]
            if nome not in pool:
                pool[nome] = {
                    "repositorio": nome,
                    "estrelas_busca": repo.get("stargazers_count")
                }

    return sorted(pool.values(), key=lambda r: r["repositorio"].lower())


def ordenar_pool(pool, semente):
    """Embaralha o pool de forma reprodutível (mesma semente → mesma ordem)."""
    ordenado = sorted(pool, key=lambda r: r["repositorio"].lower())
    random.Random(semente).shuffle(ordenado)

    for posicao, repo in enumerate(ordenado, start=1):
        repo["ordem_pool"] = posicao

    return ordenado


def candidatos(api, maximo=1000, semente=None, faixas=None):
    """Gera candidatos. Com ``semente``, em ordem aleatória reprodutível sobre a
    população completa; sem semente, mantém o comportamento da Sprint 1."""
    if semente is not None:
        for repo in ordenar_pool(montar_pool(api, faixas), semente)[:maximo]:
            yield {"full_name": repo["repositorio"], **repo}
        return

    vistos = set()
    for minimo, maximo_estrelas in faixas or FAIXAS_PADRAO:
        for repo in buscar_faixa(api, minimo, maximo_estrelas):
            nome = repo["full_name"]
            if nome in vistos:
                continue
            vistos.add(nome)
            yield repo
            if len(vistos) >= maximo:
                return


def idade_em_dias(criado_em, referencia):
    return (converter_data(referencia) - converter_data(criado_em)).days


def info_repositorio(api, nome, fim=None):
    """Metadados que custam uma única chamada (``GET /repos/{nome}``)."""
    info = api.get(f"/repos/{nome}")["data"]
    referencia = fim or datetime.now(timezone.utc)

    return {
        "repositorio": nome,
        "branch": info["default_branch"],
        "estrelas": info["stargazers_count"],
        "linguagem": info["language"],
        "criado_em": info["created_at"],
        "idade_dias": idade_em_dias(info["created_at"], referencia)
    }


def ultima_pagina(cabecalho_link):
    if not cabecalho_link:
        return None

    links = requests.utils.parse_header_links(cabecalho_link.replace(">,<", ">, <"))
    for link in links:
        if link.get("rel") == "last":
            pagina = parse_qs(urlparse(link["url"]).query).get("page")
            if pagina:
                return int(pagina[0])

    return None


def contar_contribuidores(api, nome):
    """Conta contribuidores (incluindo anônimos) com ``per_page=1``: o número
    da última página no cabeçalho ``Link`` é o total. Retorna ``None`` quando a
    API se recusa a listar (repositórios muito grandes respondem 403)."""
    try:
        resposta = api.get(
            f"/repos/{nome}/contributors",
            {"per_page": 1, "anon": "true"}
        )
    except HTTPError as erro:
        status = erro.response.status_code if erro.response is not None else None
        if status in (403, 404):
            return None
        raise

    total = ultima_pagina(resposta.get("headers", {}).get("Link"))
    if total is not None:
        return total

    dados = resposta.get("data") or []
    return len(dados)


def metadados(api, repo, fim=None):
    nome = repo["full_name"]
    dados = info_repositorio(api, nome, fim)
    dados["contribuidores"] = contar_contribuidores(api, nome)
    return dados


def possui_actions(api, repo):
    nome = repo["full_name"]
    resposta = api.get(f"/repos/{nome}/actions/workflows")
    return resposta["data"].get("total_count", 0) > 0


def selecionar_repositorios(api, quantidade=10):
    selecionados = []
    funil = {"candidatos": 0, "com_actions": 0, "sem_actions": 0}

    for repo in candidatos(api, maximo=max(quantidade * 10, 100)):
        if len(selecionados) >= quantidade:
            break

        funil["candidatos"] += 1

        if not possui_actions(api, repo):
            funil["sem_actions"] += 1
            continue

        funil["com_actions"] += 1
        selecionados.append(metadados(api, repo))

    return selecionados, funil
