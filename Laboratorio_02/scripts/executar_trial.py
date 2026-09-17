import argparse
import csv
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

TIMEBOX_SEGUNDOS = 35 * 60
INTERVALO_VERIFICACAO = 1


def executar_testes(caminho_kata):
    comando = [
        sys.executable,
        "-m",
        "pytest",
        str(caminho_kata),
        "-q",
        "--disable-warnings"
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    saida = f"{resultado.stdout}\n{resultado.stderr}"

    def quantidade(tipo):
        encontrados = re.findall(rf"(\d+)\s+{tipo}", saida)
        return int(encontrados[-1]) if encontrados else 0

    passando = quantidade("passed")
    falhando = quantidade("failed")
    erros = quantidade("error") + quantidade("errors")
    total = passando + falhando + erros

    return {
        "total": total,
        "passando": passando,
        "falhando": falhando + erros,
        "todos_passaram": resultado.returncode == 0 and passando > 0
    }


def assinatura_arquivos(caminho_kata):
    arquivos = []

    for arquivo in caminho_kata.rglob("*.py"):
        if arquivo.name.startswith("test_") or arquivo.name.endswith("_test.py"):
            continue

        try:
            arquivos.append((str(arquivo), arquivo.stat().st_mtime_ns))
        except FileNotFoundError:
            pass

    return tuple(sorted(arquivos))


def solicitar_numero_prompts(tratamento):
    if tratamento != "COM_IA":
        return 0

    while True:
        valor = input(
            "\nQuantidade de prompts/interações com a IA neste trial: "
        ).strip()

        try:
            numero = int(valor)

            if numero < 0:
                raise ValueError

            return numero
        except ValueError:
            print("Informe um número inteiro maior ou igual a zero.")


def salvar_resultado(
    arquivo_csv,
    participante,
    kata,
    tratamento,
    tempo_segundos,
    censurado,
    resultado_testes,
    inicio,
    fim,
    tempo_primeiro_teste,
    numero_iteracoes,
    numero_execucoes_testes,
    numero_prompts
):
    arquivo_csv.parent.mkdir(parents=True, exist_ok=True)
    arquivo_existe = arquivo_csv.exists()

    total = resultado_testes["total"]
    passando = resultado_testes["passando"]
    falhando = resultado_testes["falhando"]
    taxa_sucesso = (passando / total * 100) if total else 0

    linha = {
        "participante": participante,
        "kata": kata,
        "tratamento": tratamento,
        "inicio": inicio.isoformat(timespec="seconds"),
        "fim": fim.isoformat(timespec="seconds"),
        "tempo_segundos": round(tempo_segundos, 2),
        "tempo_minutos": round(tempo_segundos / 60, 2),
        "censurado": censurado,
        "testes_total": total,
        "testes_passando": passando,
        "testes_falhando": falhando,
        "taxa_sucesso_percentual": round(taxa_sucesso, 2),
        "time_to_first_pass_segundos": (
            round(tempo_primeiro_teste, 2)
            if tempo_primeiro_teste is not None
            else ""
        ),
        "time_to_first_pass_minutos": (
            round(tempo_primeiro_teste / 60, 2)
            if tempo_primeiro_teste is not None
            else ""
        ),
        "numero_iteracoes": numero_iteracoes,
        "numero_execucoes_testes": numero_execucoes_testes,
        "numero_prompts_ia": numero_prompts
    }

    with arquivo_csv.open("a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=linha.keys())

        if not arquivo_existe:
            escritor.writeheader()

        escritor.writerow(linha)


def main():
    parser = argparse.ArgumentParser(
        description="Executa e registra um trial do Laboratório 02."
    )

    parser.add_argument(
        "--participante",
        required=True,
        help="Nome do participante. Ex.: Bruna"
    )

    parser.add_argument(
        "--kata",
        required=True,
        help="Identificador do kata. Ex.: kata_01"
    )

    parser.add_argument(
        "--tratamento",
        required=True,
        choices=["COM_IA", "SEM_IA"],
        help="Tratamento utilizado no trial."
    )

    parser.add_argument(
        "--caminho-kata",
        required=True,
        help="Diretório do kata que contém a implementação e os testes."
    )

    parser.add_argument(
        "--saida",
        default="dados/resultados_trials.csv",
        help="CSV de saída. Padrão: dados/resultados_trials.csv"
    )

    args = parser.parse_args()

    caminho_kata = Path(args.caminho_kata).resolve()
    arquivo_csv = Path(args.saida).resolve()

    if not caminho_kata.exists():
        raise FileNotFoundError(f"Kata não encontrado: {caminho_kata}")

    print("=" * 60)
    print("LAB02 - EXECUÇÃO DE TRIAL")
    print("=" * 60)
    print(f"Participante : {args.participante}")
    print(f"Kata         : {args.kata}")
    print(f"Tratamento   : {args.tratamento}")
    print(f"Time-box     : {TIMEBOX_SEGUNDOS // 60} minutos")
    print(f"Resultados   : {arquivo_csv}")
    print()
    input("Pressione ENTER para iniciar o trial...")

    inicio_data = datetime.now()
    inicio = time.monotonic()

    assinatura_anterior = None
    primeira_execucao = True

    tempo_primeiro_teste = None
    numero_iteracoes = 0
    numero_execucoes_testes = 0

    ultimo_resultado = {
        "total": 0,
        "passando": 0,
        "falhando": 0,
        "todos_passaram": False
    }

    print("\nTrial iniciado. Edite normalmente o código do kata.")
    print(
        "Os testes serão executados automaticamente "
        "quando o código-fonte for salvo.\n"
    )

    try:
        while True:
            decorrido = time.monotonic() - inicio

            if decorrido >= TIMEBOX_SEGUNDOS:
                print("\nTempo limite de 35 minutos atingido.")

                ultimo_resultado = executar_testes(caminho_kata)
                numero_execucoes_testes += 1

                if (
                    tempo_primeiro_teste is None
                    and ultimo_resultado["passando"] > 0
                ):
                    tempo_primeiro_teste = TIMEBOX_SEGUNDOS

                fim_data = datetime.now()
                numero_prompts = solicitar_numero_prompts(
                    args.tratamento
                )

                salvar_resultado(
                    arquivo_csv=arquivo_csv,
                    participante=args.participante,
                    kata=args.kata,
                    tratamento=args.tratamento,
                    tempo_segundos=TIMEBOX_SEGUNDOS,
                    censurado=True,
                    resultado_testes=ultimo_resultado,
                    inicio=inicio_data,
                    fim=fim_data,
                    tempo_primeiro_teste=tempo_primeiro_teste,
                    numero_iteracoes=numero_iteracoes,
                    numero_execucoes_testes=numero_execucoes_testes,
                    numero_prompts=numero_prompts
                )

                print(
                    f"Resultado final: {ultimo_resultado['passando']}/"
                    f"{ultimo_resultado['total']} testes passando."
                )
                print("Trial registrado como censurado em 35 minutos.")
                break

            assinatura_atual = assinatura_arquivos(caminho_kata)

            if assinatura_atual != assinatura_anterior:
                assinatura_anterior = assinatura_atual

                if primeira_execucao:
                    primeira_execucao = False
                else:
                    numero_iteracoes += 1

                ultimo_resultado = executar_testes(caminho_kata)
                numero_execucoes_testes += 1

                tempo_execucao = time.monotonic() - inicio

                if (
                    tempo_primeiro_teste is None
                    and ultimo_resultado["passando"] > 0
                ):
                    tempo_primeiro_teste = tempo_execucao

                minutos = tempo_execucao / 60

                print(
                    f"[{minutos:05.2f} min] "
                    f"{ultimo_resultado['passando']}/"
                    f"{ultimo_resultado['total']} testes passando."
                )

                if ultimo_resultado["todos_passaram"]:
                    fim_data = datetime.now()
                    tempo_final = time.monotonic() - inicio

                    numero_prompts = solicitar_numero_prompts(
                        args.tratamento
                    )

                    salvar_resultado(
                        arquivo_csv=arquivo_csv,
                        participante=args.participante,
                        kata=args.kata,
                        tratamento=args.tratamento,
                        tempo_segundos=tempo_final,
                        censurado=False,
                        resultado_testes=ultimo_resultado,
                        inicio=inicio_data,
                        fim=fim_data,
                        tempo_primeiro_teste=tempo_primeiro_teste,
                        numero_iteracoes=numero_iteracoes,
                        numero_execucoes_testes=numero_execucoes_testes,
                        numero_prompts=numero_prompts
                    )

                    print("\nTodos os testes passaram.")
                    print(
                        f"Time-to-green: "
                        f"{tempo_final / 60:.2f} minutos."
                    )

                    if tempo_primeiro_teste is not None:
                        print(
                            "Time-to-first-pass: "
                            f"{tempo_primeiro_teste / 60:.2f} minutos."
                        )

                    print(
                        f"Iterações de código: {numero_iteracoes}"
                    )
                    print(
                        "Execuções automáticas de testes: "
                        f"{numero_execucoes_testes}"
                    )
                    print(
                        f"Prompts/interações com IA: {numero_prompts}"
                    )
                    print("Resultado salvo com sucesso.")
                    break

            time.sleep(INTERVALO_VERIFICACAO)

    except KeyboardInterrupt:
        print(
            "\nTrial interrompido manualmente. "
            "Nenhum resultado foi salvo."
        )


if __name__ == "__main__":
    main()
