import csv
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

ARQUIVO_JSON = os.path.join(
    DATA_DIR,
    "raw_repos.json"
)

ARQUIVO_CSV = os.path.join(
    DATA_DIR,
    "repositorios_1000.csv"
)


def carregar_repositorios():
    if not os.path.exists(ARQUIVO_JSON):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_JSON}"
        )

    with open(
        ARQUIVO_JSON,
        "r",
        encoding="utf-8"
    ) as arquivo:
        repositorios = json.load(arquivo)

    return repositorios


def calcular_razao_issues_fechadas(
    total_issues,
    closed_issues
):
    if total_issues == 0:
        return 0

    return round(
        closed_issues / total_issues,
        4
    )


def preparar_dados(repositorios):
    dados = []

    for repo in repositorios:
        primary_language = repo.get(
            "primaryLanguage"
        )

        linguagem = (
            primary_language.get("name")
            if primary_language
            else ""
        )

        total_issues = (
            repo.get("issues", {})
            .get("totalCount", 0)
        )

        closed_issues = (
            repo.get("closedIssues", {})
            .get("totalCount", 0)
        )

        merged_pull_requests = (
            repo.get("pullRequests", {})
            .get("totalCount", 0)
        )

        total_releases = (
            repo.get("releases", {})
            .get("totalCount", 0)
        )

        closed_ratio = (
            calcular_razao_issues_fechadas(
                total_issues,
                closed_issues
            )
        )

        dados.append({
            "repository": repo.get(
                "nameWithOwner",
                ""
            ),
            "created_at": repo.get(
                "createdAt",
                ""
            ),
            "updated_at": repo.get(
                "updatedAt",
                ""
            ),
            "stars": repo.get(
                "stargazerCount",
                0
            ),
            "primary_language": linguagem,
            "merged_pull_requests":
                merged_pull_requests,
            "total_releases":
                total_releases,
            "total_issues":
                total_issues,
            "closed_issues":
                closed_issues,
            "closed_ratio":
                closed_ratio
        })

    return dados


def exportar_csv(dados):
    colunas = [
        "repository",
        "created_at",
        "updated_at",
        "stars",
        "primary_language",
        "merged_pull_requests",
        "total_releases",
        "total_issues",
        "closed_issues",
        "closed_ratio"
    ]

    with open(
        ARQUIVO_CSV,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )

        writer.writeheader()
        writer.writerows(dados)


def main():
    print(
        "Carregando dados dos repositórios..."
    )

    repositorios = carregar_repositorios()

    print(
        f"{len(repositorios)} "
        f"repositórios encontrados."
    )

    if len(repositorios) != 1000:
        raise Exception(
            f"Esperados 1000 repositórios, "
            f"mas foram encontrados "
            f"{len(repositorios)}."
        )

    dados = preparar_dados(
        repositorios
    )

    exportar_csv(dados)

    print()
    print(
        "CSV exportado com sucesso!"
    )

    print(
        f"Arquivo: {ARQUIVO_CSV}"
    )

    print(
        f"Total de registros: "
        f"{len(dados)}"
    )


if __name__ == "__main__":
    main()