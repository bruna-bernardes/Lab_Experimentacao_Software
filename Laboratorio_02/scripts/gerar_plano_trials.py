import argparse
import csv
from pathlib import Path

PARTICIPANTES = ["Bruna", "Ana", "Walter"]
KATAS = ["kata_01", "kata_02", "kata_03", "kata_04"]

TRATAMENTOS = {
    "Bruna": {
        "kata_01": "COM_IA",
        "kata_02": "SEM_IA",
        "kata_03": "SEM_IA",
        "kata_04": "COM_IA",
    },
    "Ana": {
        "kata_01": "SEM_IA",
        "kata_02": "COM_IA",
        "kata_03": "COM_IA",
        "kata_04": "SEM_IA",
    },
    "Walter": {
        "kata_01": "SEM_IA",
        "kata_02": "COM_IA",
        "kata_03": "SEM_IA",
        "kata_04": "COM_IA",
    },
}

ORDENS = {
    "Bruna": ["kata_01", "kata_02", "kata_03", "kata_04"],
    "Ana": ["kata_02", "kata_03", "kata_04", "kata_01"],
    "Walter": ["kata_03", "kata_04", "kata_01", "kata_02"],
}


def gerar_plano():
    plano = []

    for participante in PARTICIPANTES:
        for ordem, kata in enumerate(ORDENS[participante], start=1):
            plano.append(
                {
                    "participante": participante,
                    "ordem": ordem,
                    "kata": kata,
                    "tratamento": TRATAMENTOS[participante][kata],
                    "timebox_minutos": 35,
                }
            )

    return plano


def validar_plano(plano):
    erros = []

    for participante in PARTICIPANTES:
        trials = [linha for linha in plano if linha["participante"] == participante]

        if len(trials) != 4:
            erros.append(
                f"{participante}: esperado 4 trials, encontrado {len(trials)}."
            )

        com_ia = sum(linha["tratamento"] == "COM_IA" for linha in trials)
        sem_ia = sum(linha["tratamento"] == "SEM_IA" for linha in trials)

        if com_ia != 2 or sem_ia != 2:
            erros.append(
                f"{participante}: esperado 2 COM_IA e 2 SEM_IA; "
                f"encontrado {com_ia} COM_IA e {sem_ia} SEM_IA."
            )

        katas_participante = {linha["kata"] for linha in trials}

        if katas_participante != set(KATAS):
            erros.append(
                f"{participante}: deve executar exatamente os quatro katas."
            )

        ordens = sorted(linha["ordem"] for linha in trials)

        if ordens != [1, 2, 3, 4]:
            erros.append(
                f"{participante}: ordem de execução inválida."
            )

    total_com_ia = sum(
        linha["tratamento"] == "COM_IA" for linha in plano
    )
    total_sem_ia = sum(
        linha["tratamento"] == "SEM_IA" for linha in plano
    )

    if total_com_ia != 6 or total_sem_ia != 6:
        erros.append(
            "O experimento deve possuir 6 trials COM_IA e 6 SEM_IA."
        )

    for kata in KATAS:
        participantes_kata = {
            linha["participante"]
            for linha in plano
            if linha["kata"] == kata
        }

        if participantes_kata != set(PARTICIPANTES):
            erros.append(
                f"{kata}: deve ser executado pelos três participantes."
            )

    if erros:
        raise ValueError(
            "Plano de trials inválido:\n- " + "\n- ".join(erros)
        )


def salvar_csv(plano, caminho_saida):
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    campos = [
        "participante",
        "ordem",
        "kata",
        "tratamento",
        "timebox_minutos",
    ]

    with caminho_saida.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(plano)


def exibir_resumo(plano):
    print("=" * 60)
    print("LAB02 - PLANO DE TRIALS")
    print("=" * 60)

    for participante in PARTICIPANTES:
        print(f"\n{participante}:")

        trials = sorted(
            (
                linha
                for linha in plano
                if linha["participante"] == participante
            ),
            key=lambda linha: linha["ordem"],
        )

        for linha in trials:
            print(
                f"  {linha['ordem']}. "
                f"{linha['kata']} - "
                f"{linha['tratamento']}"
            )

    total_com_ia = sum(
        linha["tratamento"] == "COM_IA" for linha in plano
    )
    total_sem_ia = sum(
        linha["tratamento"] == "SEM_IA" for linha in plano
    )

    print("\nResumo:")
    print(f"  Total de trials : {len(plano)}")
    print(f"  COM_IA          : {total_com_ia}")
    print(f"  SEM_IA          : {total_sem_ia}")
    print("  Time-box        : 35 minutos")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Gera e valida o plano contrabalanceado "
            "de trials do Laboratório 02."
        )
    )

    parser.add_argument(
        "--saida",
        default="dados/plano_trials.csv",
        help="Arquivo CSV de saída.",
    )

    args = parser.parse_args()

    plano = gerar_plano()
    validar_plano(plano)

    caminho_saida = Path(args.saida).resolve()
    salvar_csv(plano, caminho_saida)
    exibir_resumo(plano)

    print(f"\nPlano validado e salvo em: {caminho_saida}")


if __name__ == "__main__":
    main()
