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
    "validacao_rq03_rq04.csv"
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
        reader = csv.DictReader(arquivo)
        return list(reader)


def calcular_limites_outliers(valores):
    """
    Calcula outliers utilizando o método do intervalo interquartil (IQR).

    Limite inferior = Q1 - 1.5 * IQR
    Limite superior = Q3 + 1.5 * IQR
    """

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


def calcular_dias_desde_atualizacao(data_texto):
    if not data_texto:
        return None

    try:
        data_atualizacao = datetime.fromisoformat(
            data_texto.replace(
                "Z",
                "+00:00"
            )
        )

        agora = datetime.now(timezone.utc)

        diferenca = agora - data_atualizacao

        dias = diferenca.days

        # Uma data futura seria inconsistente
        if dias < 0:
            return None

        return dias

    except (ValueError, TypeError):
        return None


def validar_rq03(dados):
    releases = []

    valores_ausentes = 0
    sem_releases = 0

    for repo in dados:
        valor = repo.get(
            "total_releases",
            ""
        ).strip()

        if valor == "":
            valores_ausentes += 1
            continue

        try:
            total_releases = int(valor)

            releases.append(
                total_releases
            )

            if total_releases == 0:
                sem_releases += 1

        except ValueError:
            valores_ausentes += 1

    if not releases:
        raise Exception(
            "Nenhum valor válido encontrado para RQ03."
        )

    (
        q1,
        q3,
        limite_inferior,
        limite_superior
    ) = calcular_limites_outliers(releases)

    outliers = [
        valor
        for valor in releases
        if (
            valor < limite_inferior
            or valor > limite_superior
        )
    ]

    return {
        "total_analisado": len(dados),
        "valores_validos": len(releases),
        "valores_ausentes": valores_ausentes,
        "sem_releases": sem_releases,

        "minimo": min(releases),
        "maximo": max(releases),

        "media": round(
            statistics.mean(releases),
            2
        ),

        "mediana": statistics.median(
            releases
        ),

        "q1": q1,
        "q3": q3,

        "limite_inferior_outlier":
            limite_inferior,

        "limite_superior_outlier":
            limite_superior,

        "quantidade_outliers":
            len(outliers)
    }


def validar_rq04(dados):
    dias_atualizacao = []

    valores_ausentes = 0

    for repo in dados:
        data = repo.get(
            "updated_at",
            ""
        ).strip()

        dias = calcular_dias_desde_atualizacao(
            data
        )

        if dias is None:
            valores_ausentes += 1
            continue

        dias_atualizacao.append(dias)

    if not dias_atualizacao:
        raise Exception(
            "Nenhuma data válida encontrada para RQ04."
        )

    (
        q1,
        q3,
        limite_inferior,
        limite_superior
    ) = calcular_limites_outliers(
        dias_atualizacao
    )

    outliers = [
        valor
        for valor in dias_atualizacao
        if (
            valor < limite_inferior
            or valor > limite_superior
        )
    ]

    return {
        "total_analisado": len(dados),

        "valores_validos":
            len(dias_atualizacao),

        "valores_ausentes":
            valores_ausentes,

        "minimo_dias":
            min(dias_atualizacao),

        "maximo_dias":
            max(dias_atualizacao),

        "media_dias": round(
            statistics.mean(
                dias_atualizacao
            ),
            2
        ),

        "mediana_dias":
            statistics.median(
                dias_atualizacao
            ),

        "q1": q1,
        "q3": q3,

        "limite_inferior_outlier":
            limite_inferior,

        "limite_superior_outlier":
            limite_superior,

        "quantidade_outliers":
            len(outliers)
    }


def gerar_csv_validacao(dados):
    resultados = []

    releases_validos = []

    dias_validos = []

    for repo in dados:
        try:
            releases = int(
                repo.get(
                    "total_releases",
                    ""
                )
            )

            releases_validos.append(
                releases
            )

        except (ValueError, TypeError):
            pass

        dias = calcular_dias_desde_atualizacao(
            repo.get(
                "updated_at",
                ""
            )
        )

        if dias is not None:
            dias_validos.append(dias)

    (
        _,
        _,
        limite_releases_inferior,
        limite_releases_superior
    ) = calcular_limites_outliers(
        releases_validos
    )

    (
        _,
        _,
        limite_dias_inferior,
        limite_dias_superior
    ) = calcular_limites_outliers(
        dias_validos
    )

    for repo in dados:
        repository = repo.get(
            "repository",
            ""
        )

        valor_releases = repo.get(
            "total_releases",
            ""
        )

        updated_at = repo.get(
            "updated_at",
            ""
        )

        try:
            releases = int(
                valor_releases
            )

            release_ausente = False

            release_outlier = (
                releases
                < limite_releases_inferior
                or releases
                > limite_releases_superior
            )

        except (ValueError, TypeError):
            releases = ""
            release_ausente = True
            release_outlier = False

        dias = calcular_dias_desde_atualizacao(
            updated_at
        )

        atualizacao_ausente = (
            dias is None
        )

        if dias is not None:
            atualizacao_outlier = (
                dias
                < limite_dias_inferior
                or dias
                > limite_dias_superior
            )
        else:
            atualizacao_outlier = False

        resultados.append({
            "repository":
                repository,

            "total_releases":
                releases,

            "rq03_valor_ausente":
                release_ausente,

            "rq03_outlier":
                release_outlier,

            "updated_at":
                updated_at,

            "days_since_update":
                dias if dias is not None else "",

            "rq04_valor_ausente":
                atualizacao_ausente,

            "rq04_outlier":
                atualizacao_outlier
        })

    colunas = [
        "repository",
        "total_releases",
        "rq03_valor_ausente",
        "rq03_outlier",
        "updated_at",
        "days_since_update",
        "rq04_valor_ausente",
        "rq04_outlier"
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


def exibir_resultados(
    rq03,
    rq04
):
    print("=" * 60)
    print("VALIDAÇÃO RQ03")
    print("=" * 60)

    print(
        f"Total analisado: "
        f"{rq03['total_analisado']}"
    )

    print(
        f"Valores válidos: "
        f"{rq03['valores_validos']}"
    )

    print(
        f"Valores ausentes/inválidos: "
        f"{rq03['valores_ausentes']}"
    )

    print(
        f"Repositórios com 0 releases: "
        f"{rq03['sem_releases']}"
    )

    print(
        f"Mínimo de releases: "
        f"{rq03['minimo']}"
    )

    print(
        f"Máximo de releases: "
        f"{rq03['maximo']}"
    )

    print(
        f"Média: "
        f"{rq03['media']}"
    )

    print(
        f"Mediana: "
        f"{rq03['mediana']}"
    )

    print(
        f"Q1: {rq03['q1']}"
    )

    print(
        f"Q3: {rq03['q3']}"
    )

    print(
        f"Possíveis outliers: "
        f"{rq03['quantidade_outliers']}"
    )

    print()
    print("=" * 60)
    print("VALIDAÇÃO RQ04")
    print("=" * 60)

    print(
        f"Total analisado: "
        f"{rq04['total_analisado']}"
    )

    print(
        f"Datas válidas: "
        f"{rq04['valores_validos']}"
    )

    print(
        f"Datas ausentes/inválidas: "
        f"{rq04['valores_ausentes']}"
    )

    print(
        f"Atualização mais recente: "
        f"{rq04['minimo_dias']} dias"
    )

    print(
        f"Maior tempo sem atualização: "
        f"{rq04['maximo_dias']} dias"
    )

    print(
        f"Média: "
        f"{rq04['media_dias']} dias"
    )

    print(
        f"Mediana: "
        f"{rq04['mediana_dias']} dias"
    )

    print(
        f"Q1: "
        f"{rq04['q1']} dias"
    )

    print(
        f"Q3: "
        f"{rq04['q3']} dias"
    )

    print(
        f"Possíveis outliers: "
        f"{rq04['quantidade_outliers']}"
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
            f"A validação esperava 1000 "
            f"repositórios, mas encontrou "
            f"{len(dados)}."
        )

    rq03 = validar_rq03(
        dados
    )

    rq04 = validar_rq04(
        dados
    )

    gerar_csv_validacao(
        dados
    )

    print()

    exibir_resultados(
        rq03,
        rq04
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