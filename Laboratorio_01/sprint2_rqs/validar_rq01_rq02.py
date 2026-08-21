import csv
import os
import statistics
from datetime import datetime, timezone


VALIDACOES_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(VALIDACOES_DIR)

DATA_DIR = os.path.join(
    LAB_DIR,
    "data"
)

ARQUIVO_ENTRADA = os.path.join(
    DATA_DIR,
    "repositorios_1000.csv"
)

ARQUIVO_SAIDA = os.path.join(
    VALIDACOES_DIR,
    "validacao_rq01_rq02.csv"
)


def carregar_dados():
    if not os.path.exists(ARQUIVO_ENTRADA):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_ENTRADA}"
        )

    with open(
        ARQUIVO_ENTRADA,
        "r",
        encoding="utf-8-sig"
    ) as arquivo:
        return list(csv.DictReader(arquivo))


def calcular_limites_outliers(valores):
    if len(valores) < 4:
        return None, None, None, None

    quartis = statistics.quantiles(
        valores,
        n=4,
        method="inclusive"
    )

    q1 = quartis[0]
    q3 = quartis[2]

    iqr = q3 - q1

    limite_inferior = q1 - (1.5 * iqr)
    limite_superior = q3 + (1.5 * iqr)

    return (
        q1,
        q3,
        limite_inferior,
        limite_superior
    )


def calcular_idade_anos(created_at):
    if not created_at:
        return None

    try:
        data_criacao = datetime.fromisoformat(
            created_at.replace(
                "Z",
                "+00:00"
            )
        )

        agora = datetime.now(timezone.utc)

        dias = (
            agora - data_criacao
        ).days

        if dias < 0:
            return None

        return round(
            dias / 365.25,
            2
        )

    except (ValueError, TypeError):
        return None


def validar_rq01(dados):
    idades = []
    ausentes = 0

    for repo in dados:
        idade = calcular_idade_anos(
            repo.get(
                "created_at",
                ""
            ).strip()
        )

        if idade is None:
            ausentes += 1
            continue

        idades.append(idade)

    if not idades:
        raise Exception(
            "Nenhuma idade válida encontrada para RQ01."
        )

    (
        q1,
        q3,
        limite_inferior,
        limite_superior
    ) = calcular_limites_outliers(idades)

    outliers = [
        idade
        for idade in idades
        if (
            idade < limite_inferior
            or idade > limite_superior
        )
    ]

    return {
        "total_analisado": len(dados),
        "valores_validos": len(idades),
        "valores_ausentes": ausentes,
        "minimo": min(idades),
        "maximo": max(idades),
        "media": round(
            statistics.mean(idades),
            2
        ),
        "mediana": statistics.median(
            idades
        ),
        "q1": q1,
        "q3": q3,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "outliers": len(outliers)
    }


def validar_rq02(dados):
    pull_requests = []
    ausentes = 0
    zero_prs = 0

    for repo in dados:
        valor = repo.get(
            "merged_pull_requests",
            ""
        ).strip()

        if valor == "":
            ausentes += 1
            continue

        try:
            quantidade = int(valor)

            pull_requests.append(
                quantidade
            )

            if quantidade == 0:
                zero_prs += 1

        except ValueError:
            ausentes += 1

    if not pull_requests:
        raise Exception(
            "Nenhum valor válido encontrado para RQ02."
        )

    (
        q1,
        q3,
        limite_inferior,
        limite_superior
    ) = calcular_limites_outliers(
        pull_requests
    )

    outliers = [
        valor
        for valor in pull_requests
        if (
            valor < limite_inferior
            or valor > limite_superior
        )
    ]

    return {
        "total_analisado": len(dados),
        "valores_validos": len(pull_requests),
        "valores_ausentes": ausentes,
        "sem_prs_aceitas": zero_prs,
        "minimo": min(pull_requests),
        "maximo": max(pull_requests),
        "media": round(
            statistics.mean(
                pull_requests
            ),
            2
        ),
        "mediana": statistics.median(
            pull_requests
        ),
        "q1": q1,
        "q3": q3,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "outliers": len(outliers)
    }


def gerar_csv_validacao(dados):
    idades_validas = []
    prs_validas = []

    for repo in dados:
        idade = calcular_idade_anos(
            repo.get(
                "created_at",
                ""
            )
        )

        if idade is not None:
            idades_validas.append(
                idade
            )

        try:
            prs = int(
                repo.get(
                    "merged_pull_requests",
                    ""
                )
            )
            prs_validas.append(prs)

        except (ValueError, TypeError):
            pass

    (
        _,
        _,
        idade_limite_inferior,
        idade_limite_superior
    ) = calcular_limites_outliers(
        idades_validas
    )

    (
        _,
        _,
        pr_limite_inferior,
        pr_limite_superior
    ) = calcular_limites_outliers(
        prs_validas
    )

    resultados = []

    for repo in dados:
        idade = calcular_idade_anos(
            repo.get(
                "created_at",
                ""
            )
        )

        idade_ausente = (
            idade is None
        )

        idade_outlier = False

        if idade is not None:
            idade_outlier = (
                idade < idade_limite_inferior
                or idade > idade_limite_superior
            )

        try:
            prs = int(
                repo.get(
                    "merged_pull_requests",
                    ""
                )
            )

            pr_ausente = False

            pr_outlier = (
                prs < pr_limite_inferior
                or prs > pr_limite_superior
            )

        except (ValueError, TypeError):
            prs = ""
            pr_ausente = True
            pr_outlier = False

        resultados.append({
            "repository": repo.get(
                "repository",
                ""
            ),
            "created_at": repo.get(
                "created_at",
                ""
            ),
            "age_years": (
                idade
                if idade is not None
                else ""
            ),
            "rq01_valor_ausente":
                idade_ausente,
            "rq01_outlier":
                idade_outlier,
            "merged_pull_requests":
                prs,
            "rq02_valor_ausente":
                pr_ausente,
            "rq02_outlier":
                pr_outlier
        })

    colunas = [
        "repository",
        "created_at",
        "age_years",
        "rq01_valor_ausente",
        "rq01_outlier",
        "merged_pull_requests",
        "rq02_valor_ausente",
        "rq02_outlier"
    ]

    with open(
        ARQUIVO_SAIDA,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )

        writer.writeheader()
        writer.writerows(resultados)


def exibir_resultados(rq01, rq02):
    print("=" * 60)
    print("VALIDAÇÃO RQ01 - IDADE DOS REPOSITÓRIOS")
    print("=" * 60)

    print(
        f"Total analisado: "
        f"{rq01['total_analisado']}"
    )
    print(
        f"Valores válidos: "
        f"{rq01['valores_validos']}"
    )
    print(
        f"Valores ausentes/inválidos: "
        f"{rq01['valores_ausentes']}"
    )
    print(
        f"Idade mínima: "
        f"{rq01['minimo']} anos"
    )
    print(
        f"Idade máxima: "
        f"{rq01['maximo']} anos"
    )
    print(
        f"Média: "
        f"{rq01['media']} anos"
    )
    print(
        f"Mediana: "
        f"{rq01['mediana']} anos"
    )
    print(
        f"Q1: "
        f"{rq01['q1']} anos"
    )
    print(
        f"Q3: "
        f"{rq01['q3']} anos"
    )
    print(
        f"Possíveis outliers: "
        f"{rq01['outliers']}"
    )

    print()
    print("=" * 60)
    print("VALIDAÇÃO RQ02 - PULL REQUESTS ACEITAS")
    print("=" * 60)

    print(
        f"Total analisado: "
        f"{rq02['total_analisado']}"
    )
    print(
        f"Valores válidos: "
        f"{rq02['valores_validos']}"
    )
    print(
        f"Valores ausentes/inválidos: "
        f"{rq02['valores_ausentes']}"
    )
    print(
        f"Repositórios com 0 PRs aceitas: "
        f"{rq02['sem_prs_aceitas']}"
    )
    print(
        f"Mínimo: "
        f"{rq02['minimo']}"
    )
    print(
        f"Máximo: "
        f"{rq02['maximo']}"
    )
    print(
        f"Média: "
        f"{rq02['media']}"
    )
    print(
        f"Mediana: "
        f"{rq02['mediana']}"
    )
    print(
        f"Q1: "
        f"{rq02['q1']}"
    )
    print(
        f"Q3: "
        f"{rq02['q3']}"
    )
    print(
        f"Possíveis outliers: "
        f"{rq02['outliers']}"
    )


def main():
    print(
        "Carregando dados para validação..."
    )

    dados = carregar_dados()

    print(
        f"{len(dados)} repositórios carregados."
    )

    if len(dados) != 1000:
        raise Exception(
            f"Esperados 1000 repositórios, "
            f"mas foram encontrados "
            f"{len(dados)}."
        )

    rq01 = validar_rq01(dados)
    rq02 = validar_rq02(dados)

    gerar_csv_validacao(dados)

    print()

    exibir_resultados(
        rq01,
        rq02
    )

    print()
    print(
        "Validação concluída com sucesso!"
    )
    print(
        f"Arquivo gerado: "
        f"{ARQUIVO_SAIDA}"
    )


if __name__ == "__main__":
    main()