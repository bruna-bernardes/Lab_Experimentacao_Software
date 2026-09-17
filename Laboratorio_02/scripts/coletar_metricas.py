import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ARQUIVO_CONFIG_JSCPD = RAIZ_PROJETO / ".jscpd.json"
ARQUIVO_SAIDA_PADRAO = RAIZ_PROJETO / "dados" / "metricas_estaticas.csv"


def listar_arquivos_python(alvo):
    alvo = Path(alvo).resolve()

    if not alvo.exists():
        raise FileNotFoundError(f"Caminho não encontrado: {alvo}")

    if alvo.is_file():
        if alvo.suffix.lower() != ".py":
            raise ValueError("O arquivo informado deve possuir extensão .py.")
        return [alvo]

    arquivos = []

    for arquivo in alvo.rglob("*.py"):
        partes = set(arquivo.parts)

        if "__pycache__" in partes or ".venv" in partes:
            continue

        if arquivo.name.startswith("test_") or arquivo.name.endswith("_test.py"):
            continue

        arquivos.append(arquivo)

    if not arquivos:
        raise ValueError(
            "Nenhum arquivo Python de implementação foi encontrado no caminho informado."
        )

    return sorted(arquivos)


def coletar_complexidade_loc_mi(arquivos):
    complexidades = []
    loc_total = 0
    indices_manutencao = []

    for arquivo in arquivos:
        codigo = arquivo.read_text(encoding="utf-8")

        metricas_raw = analyze(codigo)
        loc_total += metricas_raw.loc

        blocos = cc_visit(codigo)

        for bloco in blocos:
            if hasattr(bloco, "methods"):
                complexidades.extend(
                    metodo.complexity for metodo in bloco.methods
                )
            else:
                complexidades.append(bloco.complexity)

        indices_manutencao.append(
            mi_visit(codigo, multi=True)
        )

    media_complexidade = (
        sum(complexidades) / len(complexidades)
        if complexidades
        else 0.0
    )

    media_mi = (
        sum(indices_manutencao) / len(indices_manutencao)
        if indices_manutencao
        else 0.0
    )

    return {
        "loc": loc_total,
        "funcoes_analisadas": len(complexidades),
        "complexidade_ciclomatica_media": round(media_complexidade, 2),
        "maintainability_index": round(media_mi, 2),
    }


def obter_cli_jscpd():
    node = shutil.which("node")

    if not node:
        raise FileNotFoundError(
            "Node.js não encontrado no PATH. Verifique com: node --version"
        )

    pasta_jscpd = RAIZ_PROJETO / "node_modules" / "jscpd"
    package_json = pasta_jscpd / "package.json"

    if not package_json.exists():
        raise FileNotFoundError(
            "jscpd não encontrado. Execute, na pasta Laboratorio_02:\n"
            "npm install --save-dev jscpd"
        )

    dados = json.loads(package_json.read_text(encoding="utf-8"))
    bin_config = dados.get("bin")

    if isinstance(bin_config, str):
        caminho_relativo = bin_config
    elif isinstance(bin_config, dict):
        caminho_relativo = (
            bin_config.get("jscpd")
            or next(iter(bin_config.values()), None)
        )
    else:
        caminho_relativo = None

    if not caminho_relativo:
        raise RuntimeError(
            "Não foi possível identificar o executável do jscpd."
        )

    cli_jscpd = (pasta_jscpd / caminho_relativo).resolve()

    if not cli_jscpd.exists():
        raise FileNotFoundError(
            f"Executável do jscpd não encontrado em: {cli_jscpd}"
        )

    return node, cli_jscpd


def coletar_duplicacao(arquivos):
    node, cli_jscpd = obter_cli_jscpd()

    with tempfile.TemporaryDirectory() as diretorio_temporario:
        diretorio_saida = Path(diretorio_temporario)

        comando = [
            node,
            str(cli_jscpd),
            *[str(arquivo) for arquivo in arquivos],
            "--config",
            str(ARQUIVO_CONFIG_JSCPD),
            "--reporters",
            "json",
            "--output",
            str(diretorio_saida),
        ]

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        relatorio = diretorio_saida / "jscpd-report.json"

        if not relatorio.exists():
            raise RuntimeError(
                "O jscpd não gerou o relatório JSON esperado.\n"
                f"Saída:\n{resultado.stdout}\n"
                f"Erro:\n{resultado.stderr}"
            )

        dados = json.loads(relatorio.read_text(encoding="utf-8"))
        total = dados.get("statistics", {}).get("total", {})

        percentual = float(total.get("percentage", 0) or 0)
        linhas_duplicadas = int(total.get("duplicatedLines", 0) or 0)

        return {
            "duplicacao_percentual": round(percentual, 2),
            "linhas_duplicadas": linhas_duplicadas,
        }


def salvar_resultado(
    arquivo_saida,
    participante,
    kata,
    tratamento,
    caminho_analisado,
    metricas,
):
    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    arquivo_existe = arquivo_saida.exists()

    linha = {
        "participante": participante,
        "kata": kata,
        "tratamento": tratamento,
        "caminho_analisado": str(caminho_analisado),
        "loc": metricas["loc"],
        "funcoes_analisadas": metricas["funcoes_analisadas"],
        "complexidade_ciclomatica_media": metricas[
            "complexidade_ciclomatica_media"
        ],
        "maintainability_index": metricas["maintainability_index"],
        "duplicacao_percentual": metricas["duplicacao_percentual"],
        "linhas_duplicadas": metricas["linhas_duplicadas"],
    }

    with arquivo_saida.open("a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=linha.keys())

        if not arquivo_existe:
            escritor.writeheader()

        escritor.writerow(linha)


def exibir_resultado(arquivos, metricas):
    print("=" * 60)
    print("LAB02 - MÉTRICAS ESTÁTICAS")
    print("=" * 60)

    print("Arquivos analisados:")
    for arquivo in arquivos:
        print(f"  - {arquivo}")

    print()
    print(f"LOC                              : {metricas['loc']}")
    print(f"Funções/métodos analisados       : {metricas['funcoes_analisadas']}")
    print(
        "Complexidade ciclomática média   : "
        f"{metricas['complexidade_ciclomatica_media']}"
    )
    print(
        "Maintainability Index            : "
        f"{metricas['maintainability_index']}"
    )
    print(
        "Duplicação de código             : "
        f"{metricas['duplicacao_percentual']}%"
    )
    print(
        "Linhas duplicadas                : "
        f"{metricas['linhas_duplicadas']}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Coleta LOC, complexidade ciclomática média, "
            "Maintainability Index e duplicação do código."
        )
    )

    parser.add_argument(
        "--arquivo",
        required=True,
        help=(
            "Arquivo .py ou diretório contendo o código de implementação. "
            "Arquivos de teste são ignorados quando um diretório é informado."
        ),
    )

    parser.add_argument("--participante", help="Nome do participante.")
    parser.add_argument("--kata", help="Identificador do kata.")

    parser.add_argument(
        "--tratamento",
        choices=["COM_IA", "SEM_IA"],
        help="Tratamento utilizado no trial.",
    )

    parser.add_argument(
        "--saida",
        default=str(ARQUIVO_SAIDA_PADRAO),
        help="CSV de saída das métricas.",
    )

    parser.add_argument(
        "--somente-exibir",
        action="store_true",
        help="Exibe as métricas sem gravar no CSV.",
    )

    args = parser.parse_args()

    arquivos = listar_arquivos_python(args.arquivo)

    metricas = coletar_complexidade_loc_mi(arquivos)
    metricas.update(coletar_duplicacao(arquivos))

    exibir_resultado(arquivos, metricas)

    if args.somente_exibir:
        print("\nResultado de teste não salvo em CSV.")
        return

    campos_obrigatorios = {
        "--participante": args.participante,
        "--kata": args.kata,
        "--tratamento": args.tratamento,
    }

    faltando = [
        campo for campo, valor in campos_obrigatorios.items() if not valor
    ]

    if faltando:
        raise ValueError(
            "Para salvar no CSV, informe: " + ", ".join(faltando)
        )

    arquivo_saida = Path(args.saida).resolve()

    salvar_resultado(
        arquivo_saida=arquivo_saida,
        participante=args.participante,
        kata=args.kata,
        tratamento=args.tratamento,
        caminho_analisado=Path(args.arquivo).resolve(),
        metricas=metricas,
    )

    print(f"\nMétricas salvas em: {arquivo_saida}")


if __name__ == "__main__":
    main()
