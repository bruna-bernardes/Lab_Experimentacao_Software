
from datetime import datetime, timezone
from urllib.parse import quote
from requests.exceptions import HTTPError


def converter_data(valor):
    if not valor:
        return None
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def coletar_releases(api, repositorio, inicio, fim):
    releases = api.paginas(f"/repos/{repositorio}/releases")
    inicio = converter_data(inicio)
    fim = converter_data(fim)

    validas = [
        r for r in releases
        if not r.get("draft")
        and not r.get("prerelease")
        and r.get("published_at")
    ]

    validas.sort(key=lambda r: r["published_at"])

    resultado = []
    for r in validas:
        data = converter_data(r["published_at"])
        if inicio <= data <= fim:
            resultado.append(r)

    return resultado


def coletar_tags(api, repositorio):
    return api.paginas(f"/repos/{repositorio}/tags")


def coletar_commits(api, repositorio, tag_anterior, tag_atual):
    base = quote(tag_anterior, safe="")
    head = quote(tag_atual, safe="")
    endpoint = f"/repos/{repositorio}/compare/{base}...{head}"
    commits = []
    pagina = 1

    while True:
        resposta = api.get(endpoint, {"per_page": 100, "page": pagina})
        dados = resposta["data"]
        lote = dados.get("commits", [])
        commits.extend(lote)

        if len(lote) < 100:
            break

        pagina += 1

    return commits


def coletar_dados_releases(api, repositorio, inicio, fim):
    todas = api.paginas(f"/repos/{repositorio}/releases")
    todas = [
        r for r in todas
        if not r.get("draft")
        and not r.get("prerelease")
        and r.get("published_at")
    ]
    todas.sort(key=lambda r: r["published_at"])

    inicio_dt = converter_data(inicio)
    fim_dt = converter_data(fim)
    resultado = []
    ignoradas = 0

    for i, release in enumerate(todas):
        data = converter_data(release["published_at"])

        if not inicio_dt <= data <= fim_dt:
            continue

        if i == 0:
            ignoradas += 1
            continue

        anterior = todas[i - 1]

        try:
            commits = coletar_commits(
                api, repositorio, anterior["tag_name"], release["tag_name"]
            )
        except HTTPError as erro:
            status = erro.response.status_code if erro.response is not None else None

            if status in (404, 422):
                ignoradas += 1
                print(f"Comparacao ignorada em {repositorio}: {anterior['tag_name']} -> {release['tag_name']} (HTTP {status})")
                continue

            raise


        resultado.append({
            "repositorio": repositorio,
            "tag": release["tag_name"],
            "tag_anterior": anterior["tag_name"],
            "published_at": release["published_at"],
            "commits": commits
        })

    return resultado, ignoradas
