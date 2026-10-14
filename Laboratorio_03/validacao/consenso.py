"""Consolidação do rótulo de consenso: ``python -m validacao.consenso``.

Protocolo (detalhado em ``validacao/protocolo_consenso.md``):
1. Unanimidade (3-0) → rótulo aceito (``origem = unanime``).
2. Maioria simples (2-1) → rótulo da maioria (``origem = maioria``).
3. Empate 1-1-1 (possível só em tipo do projeto e entregas reais) → decidido
   em reunião com os três e registrado em ``validacao/decisoes_reuniao.csv``
   (``origem = reuniao``). Se faltar alguma decisão, o script para e lista os
   itens pendentes.

Uma decisão registrada também pode substituir uma maioria, se o grupo assim
definir em reunião; nesse caso ``origem = reuniao``.
"""
import argparse
from collections import Counter
from pathlib import Path

from pipeline.arquivos import escrever_csv
from validacao.comum import AVALIADORES, NIVEIS, VOCABULARIO, ler_tabela, normalizar_rotulo
from validacao.concordancia import carregar_nivel

COLUNAS_DECISOES = ["nivel", "repositorio", "tag", "dimensao", "rotulo", "justificativa", "data", "presentes"]

COLUNAS_CONSENSO = {
    "repositorios": ["repositorio", "tipo_projeto", "origem_tipo_projeto",
                     "entregas_reais", "origem_entregas_reais"],
    "releases": ["repositorio", "tag", "corretiva", "origem_corretiva"],
}


class DecisoesPendentes(ValueError):
    pass


def voto_majoritario(rotulos):
    """``(rotulo, origem)``; ``(None, "empate")`` quando não há maioria."""
    contagem = Counter(rotulos).most_common()
    rotulo, votos = contagem[0]

    if votos == len(rotulos):
        return rotulo, "unanime"
    if votos > len(rotulos) / 2:
        return rotulo, "maioria"
    return None, "empate"


def carregar_decisoes(caminho):
    if not Path(caminho).exists():
        return {}

    decisoes = {}
    for linha in ler_tabela(caminho):
        rotulo = normalizar_rotulo(linha.get("rotulo"))
        dimensao = linha.get("dimensao", "")
        if dimensao not in VOCABULARIO or rotulo not in VOCABULARIO[dimensao]:
            raise ValueError(f"Decisão inválida em {caminho}: {linha}")
        if not linha.get("justificativa"):
            raise ValueError(f"Decisão sem justificativa em {caminho}: {linha}")
        chave = (linha["nivel"], linha["repositorio"], linha.get("tag", ""), dimensao)
        decisoes[chave] = rotulo
    return decisoes


def consolidar_nivel(rotulos, nivel, decisoes, avaliadores=AVALIADORES):
    campos_chave, dimensoes = NIVEIS[nivel]
    linhas, pendentes = [], []

    for item in sorted(rotulos[avaliadores[0]]):
        registro = dict(zip(campos_chave, item))
        for dimensao in dimensoes:
            votos = [rotulos[a][item][dimensao] for a in avaliadores]
            rotulo, origem = voto_majoritario(votos)

            chave = (nivel, registro["repositorio"], registro.get("tag", ""), dimensao)
            if chave in decisoes:
                rotulo, origem = decisoes[chave], "reuniao"
            elif rotulo is None:
                pendentes.append({**registro, "dimensao": dimensao, "votos": votos})

            registro[dimensao] = rotulo
            registro[f"origem_{dimensao}"] = origem
        linhas.append(registro)

    return linhas, pendentes


def calcular(validacao="validacao", avaliadores=AVALIADORES):
    validacao = Path(validacao)
    decisoes = carregar_decisoes(validacao / "decisoes_reuniao.csv")
    consensos, pendentes = {}, []

    for nivel in NIVEIS:
        rotulos = carregar_nivel(validacao / "rotulos", nivel, avaliadores)
        consensos[nivel], faltando = consolidar_nivel(rotulos, nivel, decisoes, avaliadores)
        pendentes.extend({"nivel": nivel, **p} for p in faltando)

    if pendentes:
        texto = "\n".join(
            f"- {p['nivel']} | {p['repositorio']} {p.get('tag', '')} | {p['dimensao']}: {p['votos']}"
            for p in pendentes)
        raise DecisoesPendentes(
            f"{len(pendentes)} empate(s) sem decisão em decisoes_reuniao.csv:\n{texto}")

    return consensos


def resumo_origens(consensos):
    contagem = Counter()
    for nivel, linhas in consensos.items():
        for linha in linhas:
            for chave, valor in linha.items():
                if chave.startswith("origem_"):
                    contagem[(chave.removeprefix("origem_"), valor)] += 1
    return contagem


def executar(validacao="validacao"):
    validacao = Path(validacao)
    if not (validacao / "decisoes_reuniao.csv").exists():
        escrever_csv(validacao / "decisoes_reuniao.csv", [], COLUNAS_DECISOES)

    consensos = calcular(validacao)
    for nivel, linhas in consensos.items():
        escrever_csv(validacao / f"consenso_{nivel}.csv", linhas, COLUNAS_CONSENSO[nivel])

    for (dimensao, origem), quantidade in sorted(resumo_origens(consensos).items()):
        print(f"{dimensao:>15} | {origem:<8} | {quantidade}")
    return consensos


def main():
    parser = argparse.ArgumentParser(description="Consolida o rótulo de consenso")
    parser.add_argument("--validacao", default="validacao")
    args = parser.parse_args()
    executar(args.validacao)


if __name__ == "__main__":
    main()
