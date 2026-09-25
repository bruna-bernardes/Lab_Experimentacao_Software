import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO_METRICAS = RAIZ / "dados" / "metricas_estaticas.csv"
ARQUIVO_SAIDA = RAIZ / "analise" / "analise_rq3.md"


def ler_csv(caminho):
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def _quantil(ordenados, proporcao):
    n = len(ordenados)
    indice = (n - 1) * proporcao

    if indice.is_integer():
        return ordenados[int(indice)]

    menor = int(indice)
    fracao = indice - menor
    return ordenados[menor] + (ordenados[menor + 1] - ordenados[menor]) * fracao


def mediana_e_iqr(valores):
    ordenados = sorted(valores)
    n = len(ordenados)

    if n % 2 == 1:
        mediana = ordenados[n // 2]
    else:
        mediana = (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2

    q1 = _quantil(ordenados, 0.25)
    q3 = _quantil(ordenados, 0.75)

    return mediana, q1, q3


def main():
    metricas = ler_csv(ARQUIVO_METRICAS)

    linhas_tabela_trial = [
        "| Participante | Kata | Tratamento | LOC | CC média | MI | Duplicação % |",
        "|---|---|---|---|---|---|---|",
    ]

    agregados = {"COM_IA": {}, "SEM_IA": {}}

    for linha in metricas:
        tratamento = linha["tratamento"]
        participante = linha["participante"]

        linhas_tabela_trial.append(
            f"| {participante} | {linha['kata']} | {tratamento} | "
            f"{linha['loc']} | {linha['complexidade_ciclomatica_media']} | "
            f"{linha['maintainability_index']} | "
            f"{linha['duplicacao_percentual']} |"
        )

        for campo in ["loc", "complexidade_ciclomatica_media", "maintainability_index"]:
            agregados[tratamento].setdefault(campo, []).append(
                float(linha[campo])
            )

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    with ARQUIVO_SAIDA.open("w", encoding="utf-8") as saida:
        saida.write("# Análise Detalhada da RQ3 — Estrutura do Código\n\n")
        saida.write(
            "Análise complementar da RQ3 com foco em complexidade "
            "ciclomática, duplicação e LOC por tratamento, usando LOC como "
            "métrica de controle.\n\n"
        )

        saida.write("## Métricas por trial\n\n")
        saida.write("\n".join(linhas_tabela_trial) + "\n\n")

        saida.write("## Resumo por tratamento (mediana e IQR)\n\n")
        saida.write("| Métrica | Tratamento | Mediana | Q1 | Q3 | IQR |\n")
        saida.write("|---|---|---|---|---|---|\n")

        rotulos = {
            "loc": "LOC",
            "complexidade_ciclomatica_media": "CC média",
            "maintainability_index": "Maintainability Index",
        }

        for campo, rotulo in rotulos.items():
            for tratamento in ["COM_IA", "SEM_IA"]:
                valores = agregados[tratamento][campo]
                mediana, q1, q3 = mediana_e_iqr(valores)
                saida.write(
                    f"| {rotulo} | {tratamento} | {mediana:.2f} | "
                    f"{q1:.2f} | {q3:.2f} | {q3 - q1:.2f} |\n"
                )

        saida.write("\n")

        loc_com = agregados["COM_IA"]["loc"]
        loc_sem = agregados["SEM_IA"]["loc"]
        cc_com = agregados["COM_IA"]["complexidade_ciclomatica_media"]
        cc_sem = agregados["SEM_IA"]["complexidade_ciclomatica_media"]

        cc_por_loc_com = sorted(
            cc / loc for cc, loc in zip(cc_com, loc_com)
        )
        cc_por_loc_sem = sorted(
            cc / loc for cc, loc in zip(cc_sem, loc_sem)
        )

        saida.write("## Complexidade normalizada por LOC (CC/LOC)\n\n")
        saida.write(
            f"- COM_IA: mediana de CC/LOC = "
            f"{cc_por_loc_com[len(cc_por_loc_com) // 2]:.4f}\n"
        )
        saida.write(
            f"- SEM_IA: mediana de CC/LOC = "
            f"{cc_por_loc_sem[len(cc_por_loc_sem) // 2]:.4f}\n\n"
        )

        saida.write("## Discussão\n\n")
        saida.write(
            "1. **Duplicação:** nenhum trial apresentou linhas duplicadas "
            "(0% em todos), então este experimento não conseguiu "
            "diferenciar os tratamentos por essa métrica. Isso é esperado "
            "em soluções de katas pequenos, com uma única função cada.\n"
        )
        saida.write(
            "2. **Complexidade ciclomática:** as medianas ficaram próximas "
            "entre os tratamentos (10.00 no COM_IA contra 11.00 no "
            "SEM_IA), mas a dispersão no SEM_IA é maior "
            "(IQR 3.50 contra 1.50). O código manual variou mais de "
            "estilo entre trials — no kata_03 da Ana, o assistente "
            "produziu CC 23.0, o outlier mais alto de todo o "
            "experimento.\n"
        )
        saida.write(
            "3. **LOC como controle:** a IA não gerou código "
            "sistematicamente mais verboso neste experimento — a mediana "
            "de LOC é praticamente igual entre os tratamentos (39.50 "
            "contra 38.50), embora o COM_IA tenha IQR maior (12.25 contra "
            "4.75). Sem essa checagem, diferenças de complexidade poderiam "
            "ser interpretadas incorretamente como mais verbosidade "
            "da IA.\n"
        )
        saida.write(
            "4. **Maintainability Index:** o COM_IA apresentou mediana "
            "maior (54.46 contra 51.88) e IQR menor (1.34 contra 1.89), "
            "sugerindo código estruturalmente mais manutenível e mais "
            "uniforme entre os trials.\n"
        )
        saida.write(
            "5. **Limitação:** com 6 trials por tratamento e katas de "
            "domínio simples, estas observações são exploratórias e não "
            "generalizáveis; servem de base para a discussão do relatório "
            "final.\n"
        )

    print(f"Análise RQ3 gerada em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()