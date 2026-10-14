"""Definições compartilhadas pela validação manual."""
import csv
from pathlib import Path

AVALIADORES = ["bruna", "ana", "walter"]

VOCABULARIO = {
    "tipo_projeto": ["biblioteca_framework", "aplicacao_servico", "ferramenta_cli", "outro"],
    "entregas_reais": ["sim", "nao", "incerto"],
    "corretiva": ["sim", "nao"],
}

# nível → (chave do item, dimensões rotuladas)
NIVEIS = {
    "repositorios": (["repositorio"], ["tipo_projeto", "entregas_reais"]),
    "releases": (["repositorio", "tag"], ["corretiva"]),
}

PASTA_ROTULOS = Path("validacao") / "rotulos"


def arquivo_rotulos(pasta, avaliador, nivel):
    return Path(pasta) / f"rotulos_{avaliador}_{nivel}.csv"


def ler_tabela(caminho):
    """Lê CSV tolerando planilhas salvas pelo Excel (separador ';' e
    codificação Windows-1252), que são comuns quando se rotula à mão."""
    bruto = Path(caminho).read_bytes()
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            texto = bruto.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue

    primeira = texto.splitlines()[0] if texto else ""
    separador = ";" if primeira.count(";") > primeira.count(",") else ","
    leitor = csv.DictReader(texto.splitlines(), delimiter=separador)
    return [{(k or "").strip(): (v or "").strip() for k, v in linha.items()} for linha in leitor]


def normalizar_rotulo(valor):
    valor = (valor or "").strip().lower()
    return (valor.replace("ã", "a").replace("ç", "c").replace("é", "e")
                 .replace("í", "i").replace("ó", "o").replace(" ", "_").replace("/", "_"))
