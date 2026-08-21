import os
import json
import time
import requests
from Laboratorio_01.códigos.config import GITHUB_TOKEN, GRAPHQL_URL, NUM_REPOS, PAGE_SIZE


def run_query(query, variables=None, max_tentativas=5):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    payload = {
        "query": query
    }

    if variables:
        payload["variables"] = variables

    for tentativa in range(1, max_tentativas + 1):
        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            if "errors" in result:
                raise Exception(
                    f"GraphQL errors: "
                    f"{json.dumps(result['errors'], indent=2)}"
                )

            return result

        if response.status_code in [502, 503, 504]:
            print(
                f"Erro temporário {response.status_code}. "
                f"Tentativa {tentativa}/{max_tentativas}..."
            )

            time.sleep(3 * tentativa)
            continue

        raise Exception(
            f"Query failed: "
            f"{response.status_code} - {response.text}"
        )

    raise Exception(
        f"Falha após {max_tentativas} tentativas."
    )


def build_search_query():
    return """
    query($cursor: String, $pageSize: Int!) {
      search(
        query: "stars:>1 sort:stars",
        type: REPOSITORY,
        first: $pageSize,
        after: $cursor
      ) {
        repositoryCount

        pageInfo {
          hasNextPage
          endCursor
        }

        nodes {
          ... on Repository {
            nameWithOwner
            createdAt
            updatedAt
            stargazerCount

            primaryLanguage {
              name
            }

            pullRequests(states: MERGED) {
              totalCount
            }

            releases {
              totalCount
            }

            issues {
              totalCount
            }

            closedIssues: issues(states: CLOSED) {
              totalCount
            }
          }
        }
      }
    }
    """


def fetch_repos(num_repos=NUM_REPOS):
    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data"
    )

    os.makedirs(data_dir, exist_ok=True)

    checkpoint_path = os.path.join(
        data_dir,
        "checkpoint_paginacao.json"
    )

    all_repos = []
    cursor = None
    pagina = 1

    # Recupera progresso anterior
    if os.path.exists(checkpoint_path):
        with open(
            checkpoint_path,
            "r",
            encoding="utf-8"
        ) as arquivo:
            checkpoint = json.load(arquivo)

        all_repos = checkpoint.get("repositorios", [])
        cursor = checkpoint.get("cursor")
        pagina = checkpoint.get("pagina", 1)

        print(
            f"Checkpoint encontrado: "
            f"{len(all_repos)} repositórios já coletados."
        )

        print(
            f"Continuando a partir da página {pagina}..."
        )

    nomes_existentes = {
        repo["nameWithOwner"]
        for repo in all_repos
        if repo and repo.get("nameWithOwner")
    }

    query = build_search_query()

    while len(all_repos) < num_repos:
        quantidade_restante = num_repos - len(all_repos)

        page_size = min(
            PAGE_SIZE,
            quantidade_restante
        )

        print(
            f"Buscando página {pagina} "
            f"({len(all_repos)}/{num_repos} "
            f"repositórios coletados)..."
        )

        variables = {
            "cursor": cursor,
            "pageSize": page_size
        }

        result = run_query(
            query,
            variables
        )

        search = result["data"]["search"]

        repos_pagina = [
            repo
            for repo in search["nodes"]
            if repo is not None
        ]

        novos_repos = 0

        for repo in repos_pagina:
            nome = repo.get("nameWithOwner")

            if not nome:
                continue

            if nome in nomes_existentes:
                continue

            all_repos.append(repo)
            nomes_existentes.add(nome)
            novos_repos += 1

        page_info = search["pageInfo"]

        cursor = page_info["endCursor"]
        pagina += 1

        checkpoint = {
            "cursor": cursor,
            "pagina": pagina,
            "repositorios": all_repos
        }

        with open(
            checkpoint_path,
            "w",
            encoding="utf-8"
        ) as arquivo:
            json.dump(
                checkpoint,
                arquivo,
                indent=2,
                ensure_ascii=False
            )

        print(
            f"Página concluída. "
            f"{novos_repos} novos repositórios. "
            f"Total salvo: "
            f"{len(all_repos)}/{num_repos}"
        )

        if not page_info["hasNextPage"]:
            print(
                "A paginação principal informou "
                "que não existem mais páginas."
            )
            break
          
    if len(all_repos) < num_repos and all_repos:
        faltantes = num_repos - len(all_repos)

        ultima_quantidade_estrelas = all_repos[-1].get(
            "stargazerCount",
            0
        )

        print()
        print(
            f"A coleta principal terminou com "
            f"{len(all_repos)} repositórios."
        )

        print(
            f"Ainda faltam {faltantes}. "
            f"Iniciando busca complementar..."
        )

        query_complementar = """
        query(
            $cursor: String,
            $pageSize: Int!,
            $searchQuery: String!
        ) {
          search(
            query: $searchQuery,
            type: REPOSITORY,
            first: $pageSize,
            after: $cursor
          ) {
            pageInfo {
              hasNextPage
              endCursor
            }

            nodes {
              ... on Repository {
                nameWithOwner
                createdAt
                updatedAt
                stargazerCount

                primaryLanguage {
                  name
                }

                pullRequests(states: MERGED) {
                  totalCount
                }

                releases {
                  totalCount
                }

                issues {
                  totalCount
                }

                closedIssues: issues(states: CLOSED) {
                  totalCount
                }
              }
            }
          }
        }
        """

        cursor_complementar = None

        search_query = (
            f"stars:0..{ultima_quantidade_estrelas} "
            f"sort:stars-desc"
        )

        while len(all_repos) < num_repos:
            quantidade_restante = (
                num_repos - len(all_repos)
            )

            page_size = min(
                PAGE_SIZE,
                quantidade_restante
            )

            print(
                f"Complementando coleta: "
                f"{len(all_repos)}/{num_repos}"
            )

            variables = {
                "cursor": cursor_complementar,
                "pageSize": page_size,
                "searchQuery": search_query
            }

            result = run_query(
                query_complementar,
                variables
            )

            search = result["data"]["search"]

            adicionados = 0

            for repo in search["nodes"]:
                if repo is None:
                    continue

                nome = repo.get("nameWithOwner")

                if not nome:
                    continue

                if nome in nomes_existentes:
                    continue

                all_repos.append(repo)
                nomes_existentes.add(nome)
                adicionados += 1

                if len(all_repos) >= num_repos:
                    break

            checkpoint = {
                "cursor": cursor,
                "pagina": pagina,
                "repositorios": all_repos
            }

            with open(
                checkpoint_path,
                "w",
                encoding="utf-8"
            ) as arquivo:
                json.dump(
                    checkpoint,
                    arquivo,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"{adicionados} novos repositórios "
                f"adicionados."
            )

            if len(all_repos) >= num_repos:
                break

            page_info = search["pageInfo"]

            if not page_info["hasNextPage"]:
                break

            cursor_complementar = (
                page_info["endCursor"]
            )
    repos = all_repos[:num_repos]

    if len(repos) == num_repos:
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

        print()
        print(
            f"Coleta concluída com sucesso: "
            f"{len(repos)} repositórios."
        )

        print(
            "Checkpoint removido, pois a coleta "
            "foi concluída."
        )

        return repos

    raise Exception(
        f"Coleta incompleta. "
        f"Foram obtidos {len(repos)} de "
        f"{num_repos} repositórios."
    )


def buscar_repositorios_restantes(all_repos, num_repos):
    if len(all_repos) >= num_repos:
        return all_repos[:num_repos]

    nomes_existentes = {
        repo["nameWithOwner"]
        for repo in all_repos
    }

    ultima_quantidade_estrelas = all_repos[-1]["stargazerCount"]

    print()
    print(
        f"Buscando repositorios restantes a partir de "
        f"{ultima_quantidade_estrelas} estrelas..."
    )

    cursor = None

    while len(all_repos) < num_repos:
        query = """
        query($cursor: String, $pageSize: Int!, $searchQuery: String!) {
          search(
            query: $searchQuery,
            type: REPOSITORY,
            first: $pageSize,
            after: $cursor
          ) {
            pageInfo {
              hasNextPage
              endCursor
            }

            nodes {
              ... on Repository {
                nameWithOwner
                createdAt
                updatedAt
                stargazerCount

                primaryLanguage {
                  name
                }

                pullRequests(states: MERGED) {
                  totalCount
                }

                releases {
                  totalCount
                }

                issues {
                  totalCount
                }

                closedIssues: issues(states: CLOSED) {
                  totalCount
                }
              }
            }
          }
        }
        """

        variables = {
            "cursor": cursor,
            "pageSize": 10,
            "searchQuery": (
                f"stars:<={ultima_quantidade_estrelas} "
                f"sort:stars-desc"
            )
        }

        result = run_query(query, variables)

        search = result["data"]["search"]

        for repo in search["nodes"]:
            if repo is None:
                continue

            nome = repo["nameWithOwner"]

            if nome in nomes_existentes:
                continue

            all_repos.append(repo)
            nomes_existentes.add(nome)

            print(
                f"Complementando: "
                f"{len(all_repos)}/{num_repos}"
            )

            if len(all_repos) >= num_repos:
                break

        if len(all_repos) >= num_repos:
            break

        if not search["pageInfo"]["hasNextPage"]:
            break

        cursor = search["pageInfo"]["endCursor"]

    return all_repos[:num_repos]


if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print(
            "ERRO: Defina a variável de ambiente GITHUB_TOKEN."
        )
        print(
            "Exemplo: export GITHUB_TOKEN=ghp_seutokenaqui"
        )
        exit(1)

    repos = fetch_repos()

    with open(
        "data/raw_repos.json",
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            repos,
            arquivo,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Coletados {len(repos)} repositórios com sucesso!"
    )