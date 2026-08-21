import csv
import os
import statistics
from collections import Counter


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
    "validacao_rq05_rq06.csv"
)


# Deve permanecer consistente com a referência
# usada pelo grupo para linguagens populares.
POPULAR_LANGUAGES_TIOBE = {
    "Python",
    "C++",
    "C",
    "Java",
    "C#",
    "JavaScript",
    "Visual Basic",
    "Go",
    "SQL",
    "Delphi/Object Pascal"
}


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


def validar_rq05(dados):
    linguagens = []
    ausentes = 0

    for repo in dados:
        linguagem = repo.get(
            "primary_language",
            ""
        ).strip()

        if not linguagem:
            ausentes += 1
            continue

        linguagens.append(
            linguagem
        )

    distribuicao = Counter(
        linguagens
    )

    populares = sum(
        quantidade
        for linguagem, quantidade
        in distribuicao.items()
        if linguagem
        in POPULAR_LANGUAGES_TIOBE
    )

    nao_populares = (
        len(linguagens)
        - populares
    )

    return {
        "total_analisado": len(dados),
        "valores_validos": len(linguagens),
        "valores_ausentes": ausentes,
        "linguagens_distintas":
            len(distribuicao),
        "repos_linguagem_popular":
            populares,
        "repos_linguagem_nao_popular":
            nao_populares,
        "top_linguagens":
            distribuicao.most_common(10)
    }


def validar_rq06(dados):
    razoes = []

    ausentes = 0
    inconsistentes = 0
    sem_issues = 0

    for repo in dados:
        try:
            total_issues = int(
                repo.get(
                    "total_issues",
                    ""
                )
            )

            closed_issues = int(
                repo.get(
                    "closed_issues",
                    ""
                )
            )

        except (ValueError, TypeError):
            ausentes += 1
            continue

        if total_issues < 0:
            inconsistentes += 1
            continue

        if closed_issues < 0:
            inconsistentes += 1
            continue

        if closed_issues > total_issues:
            inconsistentes += 1
            continue

        if total_issues == 0:
            sem_issues += 1
            razao = 0
        else:
            razao = (
                closed_issues
                / total_issues
            )

        razoes.append(
            razao
        )

    if not razoes:
        raise Exception(
            "Nenhuma razão válida encontrada para RQ06."
        )

    (
        q1,
        q3,
        limite_inferior,
        limite_superior
    ) = calcular_limites_outliers(
        razoes
    )

    outliers = [
        valor
        for valor in razoes
        if (
            valor < limite_inferior
            or valor > limite_superior
        )
    ]

    return {
        "total_analisado": len(dados),
        "valores_validos": len(razoes),
        "valores_ausentes": ausentes,
        "valores_inconsistentes":
            inconsistentes,
        "repositorios_sem_issues":
            sem_issues,
        "minimo": round(
            min(razoes),
            4
        ),
        "maximo": round(
            max(razoes),
            4
        ),
        "media": round(
            statistics.mean(
                razoes
            ),
            4
        ),
        "mediana": round(
            statistics.median(
                razoes
            ),
            4
        ),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "limite_inferior":
            limite_inferior,
        "limite_superior":
            limite_superior,
        "outliers":
            len(outliers)
    }


def gerar_csv_validacao(dados):
    razoes_validas = []

    for repo in dados:
        try:
            total_issues = int(
                repo.get(
                    "total_issues",
                    ""
                )
            )

            closed_issues = int(
                repo.get(
                    "closed_issues",
                    ""
                )
            )

            if (
                total_issues >= 0
                and closed_issues >= 0
                and closed_issues <= total_issues
            ):
                if total_issues == 0:
                    razao = 0
                else:
                    razao = (
                        closed_issues
                        / total_issues
                    )

                razoes_validas.append(
                    razao
                )

        except (ValueError, TypeError):
            pass

    (
        _,
        _,
        limite_inferior,
        limite_superior
    ) = calcular_limites_outliers(
        razoes_validas
    )

    resultados = []

    for repo in dados:
        linguagem = repo.get(
            "primary_language",
            ""
        ).strip()

        linguagem_ausente = (
            linguagem == ""
        )

        linguagem_popular = (
            linguagem
            in POPULAR_LANGUAGES_TIOBE
            if linguagem
            else False
        )

        try:
            total_issues = int(
                repo.get(
                    "total_issues",
                    ""
                )
            )

            closed_issues = int(
                repo.get(
                    "closed_issues",
                    ""
                )
            )

            inconsistente = (
                total_issues < 0
                or closed_issues < 0
                or closed_issues > total_issues
            )

            if not inconsistente:
                if total_issues == 0:
                    razao = 0
                else:
                    razao = (
                        closed_issues
                        / total_issues
                    )

                valor_ausente = False

                outlier = (
                    razao < limite_inferior
                    or razao > limite_superior
                )

            else:
                razao = ""
                valor_ausente = False
                outlier = False

        except (ValueError, TypeError):
            total_issues = ""
            closed_issues = ""
            razao = ""
            valor_ausente = True
            inconsistente = False
            outlier = False

        resultados.append({
            "repository":
                repo.get(
                    "repository",
                    ""
                ),

            "primary_language":
                linguagem,

            "rq05_valor_ausente":
                linguagem_ausente,

            "rq05_linguagem_popular":
                linguagem_popular,

            "total_issues":
                total_issues,

            "closed_issues":
                closed_issues,

            "closed_ratio":
                (
                    round(razao, 4)
                    if razao != ""
                    else ""
                ),

            "rq06_valor_ausente":
                valor_ausente,

            "rq06_inconsistente":
                inconsistente,

            "rq06_outlier":
                outlier
        })

    colunas = [
        "repository",
        "primary_language",
        "rq05_valor_ausente",
        "rq05_linguagem_popular",
        "total_issues",
        "closed_issues",
        "closed_ratio",
        "rq06_valor_ausente",
        "rq06_inconsistente",
        "rq06_outlier"
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


def exibir_resultados(rq05, rq06):
    print("=" * 60)
    print("VALIDAÇÃO RQ05 - LINGUAGEM PRIMÁRIA")
    print("=" * 60)

    print(
        f"Total analisado: "
        f"{rq05['total_analisado']}"
    )

    print(
        f"Valores válidos: "
        f"{rq05['valores_validos']}"
    )

    print(
        f"Valores ausentes: "
        f"{rq05['valores_ausentes']}"
    )

    print(
        f"Linguagens distintas: "
        f"{rq05['linguagens_distintas']}"
    )

    print(
        f"Repositórios em linguagens populares: "
        f"{rq05['repos_linguagem_popular']}"
    )

    print(
        f"Repositórios em outras linguagens: "
        f"{rq05['repos_linguagem_nao_popular']}"
    )

    print()
    print("10 linguagens mais frequentes:")

    for linguagem, quantidade in rq05[
        "top_linguagens"
    ]:
        classificacao = (
            "POPULAR"
            if linguagem
            in POPULAR_LANGUAGES_TIOBE
            else "não popular"
        )

        print(
            f"  {linguagem}: "
            f"{quantidade} "
            f"({classificacao})"
        )

    print()
    print("=" * 60)
    print("VALIDAÇÃO RQ06 - ISSUES FECHADAS")
    print("=" * 60)

    print(
        f"Total analisado: "
        f"{rq06['total_analisado']}"
    )

    print(
        f"Valores válidos: "
        f"{rq06['valores_validos']}"
    )

    print(
        f"Valores ausentes: "
        f"{rq06['valores_ausentes']}"
    )

    print(
        f"Valores inconsistentes: "
        f"{rq06['valores_inconsistentes']}"
    )

    print(
        f"Repositórios sem issues: "
        f"{rq06['repositorios_sem_issues']}"
    )

    print(
        f"Razão mínima: "
        f"{rq06['minimo']}"
    )

    print(
        f"Razão máxima: "
        f"{rq06['maximo']}"
    )

    print(
        f"Média: "
        f"{rq06['media']}"
    )

    print(
        f"Mediana: "
        f"{rq06['mediana']}"
    )

    print(
        f"Q1: "
        f"{rq06['q1']}"
    )

    print(
        f"Q3: "
        f"{rq06['q3']}"
    )

    print(
        f"Possíveis outliers: "
        f"{rq06['outliers']}"
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

    rq05 = validar_rq05(dados)
    rq06 = validar_rq06(dados)

    gerar_csv_validacao(dados)

    print()

    exibir_resultados(
        rq05,
        rq06
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