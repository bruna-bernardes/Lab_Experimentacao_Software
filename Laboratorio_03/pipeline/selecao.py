
from datetime import datetime, timezone


def buscar_faixa(api, minimo, maximo):
    parametros = {
        "q": f"stars:{minimo}..{maximo} archived:false fork:false",
        "sort": "updated",
        "order": "desc",
        "per_page": 100
    }

    resposta = api.get("/search/repositories", parametros)
    total = resposta["data"].get("total_count", 0)

    if total > 1000:
        if minimo == maximo:
            raise RuntimeError(f"Mais de 1000 repositorios com {minimo} estrelas.")

        meio = (minimo + maximo) // 2
        yield from buscar_faixa(api, minimo, meio)
        yield from buscar_faixa(api, meio + 1, maximo)
    else:
        yield from api.paginas("/search/repositories", parametros, limite=1000)


def candidatos(api, maximo=1000):
    vistos = set()
    faixas = [
        (1001, 2000),
        (2001, 5000),
        (5001, 10000),
        (10001, 1000000)
    ]

    for minimo, maximo_estrelas in faixas:
        for repo in buscar_faixa(api, minimo, maximo_estrelas):
            nome = repo["full_name"]

            if nome in vistos:
                continue

            vistos.add(nome)
            yield repo

            if len(vistos) >= maximo:
                return


def metadados(api, repo):
    nome = repo["full_name"]
    info = api.get(f"/repos/{nome}")["data"]
    contrib = api.paginas(
        f"/repos/{nome}/contributors",
        {"per_page": 100, "anon": "true"}
    )

    criado = datetime.fromisoformat(info["created_at"].replace("Z", "+00:00"))

    return {
        "repositorio": nome,
        "branch": info["default_branch"],
        "estrelas": info["stargazers_count"],
        "linguagem": info["language"],
        "contribuidores": len(contrib),
        "idade_dias": (datetime.now(timezone.utc) - criado).days
    }


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
