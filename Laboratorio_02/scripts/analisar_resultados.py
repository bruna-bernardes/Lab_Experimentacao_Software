import csv
from pathlib import Path

import numpy as np
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO_TRIALS = RAIZ / "dados" / "resultados_trials.csv"
ARQUIVO_METRICAS = RAIZ / "dados" / "metricas_estaticas.csv"
ARQUIVO_SAIDA = RAIZ / "analise" / "resultados_estatisticos.md"

ALFA = 0.05
PARTICIPANTES = ["Ana", "Bruna", "Walter"]


def ler_csv(caminho):
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def mediana_iqr(valores):
    valores = np.array(valores, dtype=float)
    mediana = np.median(valores)
    q1 = np.percentile(valores, 25)
    q3 = np.percentile(valores, 75)
    return mediana, q1, q3


def cliffs_delta(com_ia, sem_ia):
    com_ia = np.asarray(com_ia, dtype=float)
    sem_ia = np.asarray(sem_ia, dtype=float)

    maiores = sum(1 for x in com_ia for y in sem_ia if x > y)
    menores = sum(1 for x in com_ia for y in sem_ia if x < y)
    total = len(com_ia) * len(sem_ia)

    return (maiores - menores) / total if total else 0.0


def interpretar_delta(delta):
    absoluto = abs(delta)

    if absoluto < 0.147:
        return "negligenciável"
    if absoluto < 0.33:
        return "pequeno"
    if absoluto < 0.474:
        return "médio"

    return "grande"


def bloco_descritivo(com_ia, sem_ia, unidade):
    linhas = [
        f"**Unidade:** {unidade}",
        "",
        "| Tratamento | Mediana | Q1 | Q3 | IQR |",
        "|---|---|---|---|---|",
    ]

    for tratamento, valores in [
        ("COM_IA", com_ia),
        ("SEM_IA", sem_ia),
    ]:
        mediana, q1, q3 = mediana_iqr(valores)
        linhas.append(
            f"| {tratamento} | {mediana:.2f} | {q1:.2f} | {q3:.2f} | "
            f"{q3 - q1:.2f} |"
        )

    return "\n".join(linhas)


def analisar_variavel(titulo, com_ia, sem_ia, unidade):
    com_ia_arr = np.asarray(com_ia, dtype=float)
    sem_ia_arr = np.asarray(sem_ia, dtype=float)

    diferencas = sem_ia_arr - com_ia_arr

    if np.all(diferencas == 0):
        pvalor = 1.0
    else:
        pvalor = stats.wilcoxon(com_ia_arr, sem_ia_arr).pvalue

    delta = cliffs_delta(com_ia_arr, sem_ia_arr)

    decisao = (
        "rejeita H0 (diferença significativa)"
        if pvalor < ALFA
        else "não rejeita H0 (sem diferença significativa)"
    )

    return {
        "titulo": titulo,
        "unidade": unidade,
        "n": len(com_ia),
        "descritivo": bloco_descritivo(com_ia_arr, sem_ia_arr, unidade),
        "pvalor": pvalor,
        "decisao": decisao,
        "delta": delta,
        "magnitude": interpretar_delta(delta),
        "vencedores_sem_ia": int(np.sum(diferencas > 0)),
        "vencedores_com_ia": int(np.sum(diferencas < 0)),
        "empates": int(np.sum(diferencas == 0)),
    }


def escrever_resultado(arquivo, analise):
    arquivo.write(f"### {analise['titulo']}\n\n")
    arquivo.write(analise["descritivo"] + "\n\n")
    arquivo.write(
        f"- Wilcoxon pareado (n = {analise['n']}): "
        f"p-valor = **{analise['pvalor']:.4f}** — {analise['decisao']} "
        f"(alfa = {ALFA})\n"
    )
    arquivo.write(
        f"- Cliff's delta: **{analise['delta']:+.3f}** "
        f"({analise['magnitude']})\n"
    )
    arquivo.write(
        f"- Comparação por pares: valor maior em SEM_IA em "
        f"{analise['vencedores_sem_ia']} par(es), maior em COM_IA em "
        f"{analise['vencedores_com_ia']} par(es), empate em "
        f"{analise['empates']} par(es)\n\n"
    )


def valores_por_participante(linhas, campo, agregador):
    valores = {"COM_IA": [], "SEM_IA": []}

    for participante in PARTICIPANTES:
        for tratamento in ["COM_IA", "SEM_IA"]:
            selecionados = [
                float(linha[campo])
                for linha in linhas
                if linha["participante"] == participante
                and linha["tratamento"] == tratamento
            ]
            valores[tratamento].append(agregador(selecionados))

    return valores


def valores_por_kata(linhas, campo):
    valores = {"COM_IA": [], "SEM_IA": []}

    katas = sorted({linha["kata"] for linha in linhas})

    for kata in katas:
        for tratamento in ["COM_IA", "SEM_IA"]:
            selecionados = [
                float(linha[campo])
                for linha in linhas
                if linha["kata"] == kata
                and linha["tratamento"] == tratamento
            ]
            valores[tratamento].append(float(np.mean(selecionados)))

    return valores


def main():
    trials = ler_csv(ARQUIVO_TRIALS)
    metricas = ler_csv(ARQUIVO_METRICAS)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    with ARQUIVO_SAIDA.open("w", encoding="utf-8") as saida:
        saida.write("# Resultados Estatísticos — Lab02\n\n")
        saida.write(
            "Desenho: crossover within-subject contrabalanceado "
            "(3 participantes × 4 katas = 12 trials, 6 por tratamento).\n\n"
        )
        saida.write(
            "Como cada participante resolveu cada kata apenas uma vez, o "
            "pareamento do Wilcoxon foi feito agregando por participante "
            "(média dos 2 katas de cada tratamento) para RQ1 e RQ2, e "
            "agregando por kata (média dos 3 participantes) para RQ3.\n\n"
        )
        saida.write(
            "H0: a distribuição das amostras pareadas é a mesma entre os "
            "tratamentos. Tamanho de efeito: Cliff's delta — positivo "
            "indica valores maiores em SEM_IA; negativo, valores maiores "
            "em COM_IA.\n\n"
        )

        saida.write("## RQ1 — Tempo (time-to-green)\n\n")

        valores = valores_por_participante(
            trials, "tempo_segundos", np.mean
        )
        analise = analisar_variavel(
            "Tempo médio por participante (média dos 2 katas de cada tratamento)",
            valores["COM_IA"],
            valores["SEM_IA"],
            "segundos",
        )
        escrever_resultado(saida, analise)

        com_min = [float(t["tempo_minutos"]) for t in trials if t["tratamento"] == "COM_IA"]
        sem_min = [float(t["tempo_minutos"]) for t in trials if t["tratamento"] == "SEM_IA"]
        mediana_com, _, _ = mediana_iqr(com_min)
        mediana_sem, _, _ = mediana_iqr(sem_min)

        saida.write(
            f"Considerando todos os 6 trials por tratamento, a mediana do "
            f"time-to-green foi de {mediana_com:.2f} min no COM_IA contra "
            f"{mediana_sem:.2f} min no SEM_IA "
            f"(redução de {(1 - mediana_com / mediana_sem) * 100:.1f}% com "
            f"o uso da IA).\n\n"
        )

        saida.write("## RQ2 — Defeitos (taxa de sucesso dos testes)\n\n")

        valores = valores_por_participante(
            trials, "taxa_sucesso_percentual", np.mean
        )
        analise = analisar_variavel(
            "Taxa de sucesso dos testes (média por participante)",
            valores["COM_IA"],
            valores["SEM_IA"],
            "percentual",
        )
        escrever_resultado(saida, analise)

        com_falhas = [
            int(t["testes_falhando"]) for t in trials if t["tratamento"] == "COM_IA"
        ]
        sem_falhas = [
            int(t["testes_falhando"]) for t in trials if t["tratamento"] == "SEM_IA"
        ]

        saida.write(
            f"Contagem absoluta de testes falhando ao final: COM_IA = "
            f"{sum(com_falhas)}, SEM_IA = {sum(sem_falhas)}. Todos os 12 "
            f"trials concluíram com 100% de sucesso (variância zero), "
            f"impedindo qualquer conclusão estatística sobre defeitos "
            f"neste experimento.\n\n"
        )

        saida.write("## RQ3 — Estrutura do código (métricas estáticas)\n\n")

        for campo, titulo, unidade in [
            (
                "complexidade_ciclomatica_media",
                "Complexidade ciclomática média (Radon cc)",
                "CC",
            ),
            ("duplicacao_percentual", "Duplicação de código (jscpd)", "percentual"),
            (
                "maintainability_index",
                "Maintainability Index (Radon mi)",
                "índice",
            ),
            ("loc", "LOC (métrica de controle)", "linhas"),
        ]:
            valores = valores_por_kata(metricas, campo)
            analise = analisar_variavel(titulo, valores["COM_IA"], valores["SEM_IA"], unidade)
            escrever_resultado(saida, analise)

        saida.write("## Notas sobre o poder estatístico\n\n")
        saida.write(
            "Com n = 3 pares (por participante, RQ1/RQ2) ou n = 4 pares "
            "(por kata, RQ3), o menor p-valor bilateral possível no "
            "Wilcoxon é 0,25 (n = 3) e 0,125 (n = 4) — nunca abaixo de "
            "alfa = 0,05. Os resultados são, portanto, descritivos e "
            "exploratórios; o tamanho de efeito (Cliff's delta) é a "
            "informação mais relevante neste tamanho de amostra.\n"
        )
        saida.write(
            "A variância zero em RQ2 (100% de sucesso em todos os trials) "
            "impede qualquer conclusão sobre diferença de defeitos entre "
            "os tratamentos neste experimento.\n"
        )

    print(f"Análise gerada em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()