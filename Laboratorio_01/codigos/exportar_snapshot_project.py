import csv
import json
import os
import subprocess
import requests


GRAPHQL_URL = "https://api.github.com/graphql"

NOME_PROJECT = "Laboratório de Experimentação de Software"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPO_DIR = os.path.dirname(BASE_DIR)

PASTA_SNAPSHOTS = os.path.join(
    REPO_DIR,
    "snapshots"
)

SPRINT = "Lab01S03"


def obter_token():
    resultado = subprocess.run(
        ["gh", "auth", "token"],
        capture_output=True,
        text=True,
        check=True
    )

    token = resultado.stdout.strip()

    if not token:
        raise Exception("Não foi possível obter o token do GitHub CLI.")

    return token


def executar_graphql(query, variables=None):
    token = obter_token()

    response = requests.post(
        GRAPHQL_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "query": query,
            "variables": variables or {}
        }
    )

    if response.status_code != 200:
        raise Exception(
            f"Erro HTTP {response.status_code}: {response.text}"
        )

    resultado = response.json()

    if "errors" in resultado:
        raise Exception(
            json.dumps(
                resultado["errors"],
                indent=2,
                ensure_ascii=False
            )
        )

    return resultado["data"]


def localizar_project():
    query = """
    query {
      viewer {
        projectsV2(first: 100) {
          nodes {
            id
            number
            title
          }
        }
      }
    }
    """

    dados = executar_graphql(query)

    projetos = dados["viewer"]["projectsV2"]["nodes"]

    for projeto in projetos:
        if projeto["title"] == NOME_PROJECT:
            return projeto

    raise Exception(
        f"Project '{NOME_PROJECT}' não encontrado."
    )


def buscar_itens(project_id):
    query = """
    query($projectId: ID!, $cursor: String) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }

            nodes {
              content {
                __typename

                ... on Issue {
                  number
                  title
                  url

                  repository {
                    name
                  }

                  assignees(first: 20) {
                    nodes {
                      login
                    }
                  }
                }

                ... on PullRequest {
                  number
                  title
                  url

                  repository {
                    name
                  }

                  assignees(first: 20) {
                    nodes {
                      login
                    }
                  }
                }

                ... on DraftIssue {
                  title
                }
              }

              fieldValues(first: 50) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name

                    field {
                      ... on ProjectV2SingleSelectField {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    itens = []
    cursor = None

    while True:
        dados = executar_graphql(
            query,
            {
                "projectId": project_id,
                "cursor": cursor
            }
        )

        resultado = dados["node"]["items"]

        itens.extend(resultado["nodes"])

        if not resultado["pageInfo"]["hasNextPage"]:
            break

        cursor = resultado["pageInfo"]["endCursor"]

    return itens


def obter_status(item):
    for valor in item["fieldValues"]["nodes"]:
        campo = valor.get("field")

        if campo and campo.get("name") == "Status":
            return valor.get("name", "")

    return ""


def preparar_linhas(itens):
    linhas = []

    for item in itens:
        conteudo = item.get("content")

        if not conteudo:
            continue

        tipo = conteudo.get("__typename", "")

        repositorio = ""

        if conteudo.get("repository"):
            repositorio = conteudo["repository"]["name"]

        responsaveis = ""

        if conteudo.get("assignees"):
            responsaveis = ", ".join(
                pessoa["login"]
                for pessoa in conteudo["assignees"]["nodes"]
            )

        linhas.append({
            "tipo": tipo,
            "repositorio": repositorio,
            "numero": conteudo.get("number", ""),
            "titulo": conteudo.get("title", ""),
            "status": obter_status(item),
            "responsaveis": responsaveis,
            "url": conteudo.get("url", "")
        })

    return linhas


def salvar_csv(linhas):
    os.makedirs(
        PASTA_SNAPSHOTS,
        exist_ok=True
    )

    caminho = os.path.join(
        PASTA_SNAPSHOTS,
        f"{SPRINT}.csv"
    )

    colunas = [
        "tipo",
        "repositorio",
        "numero",
        "titulo",
        "status",
        "responsaveis",
        "url"
    ]

    with open(
        caminho,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )

        writer.writeheader()
        writer.writerows(linhas)

    return caminho


def main():
    print("Localizando GitHub Project...")

    projeto = localizar_project()

    print(
        f"Project encontrado: "
        f"{projeto['title']} "
        f"(#{projeto['number']})"
    )

    print("Coletando itens do Project...")

    itens = buscar_itens(
        projeto["id"]
    )

    print(
        f"{len(itens)} itens encontrados."
    )

    linhas = preparar_linhas(itens)

    caminho = salvar_csv(linhas)

    print()
    print("Snapshot exportado com sucesso!")
    print(f"Arquivo: {caminho}")


if __name__ == "__main__":
    main()