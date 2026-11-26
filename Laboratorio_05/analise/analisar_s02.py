"""Análise da amostra confirmatória da Sprint 2.

Responsável: Walter Louback (análise e impacto).

Lê as duas janelas validadas. Cada página entra uma vez: mediana das três
repetições dentro da janela e, depois, mediana dessas duas medianas.
As hipóteses e a rubrica são as da proposta da Sprint 1.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

PASTA_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PASTA_LAB / "instrumentacao"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analisar_piloto import (  # noqa: E402
    ALFA,
    P0_CONJUNTO_MINIMO,
    PESSOAS_ACESSO_UNICO_MARCO_2026,
    _fmt,
    _fmt_p,
    _grafico,
    _linha_comparacao,
    _periodo_local,
    agregar_paginas,
    comparar_grupos,
    horas_coletivas,
    resumir,
    tamanho_amostra_proporcao,
    teste_binomial,
    teste_z_proporcao,
)
from coleta_s02 import JANELAS, caminhos_s02  # noqa: E402
from medicao import ITENS_CONJUNTO_MINIMO, ITENS_PONTUACAO, ler_urls  # noqa: E402
from validar_s02 import validar_janela  # noqa: E402

CAMPOS_MEDIANA = (
    "tempo_total_ms",
    "ttfb_ms",
    "tempo_tls_ms",
    "bytes_transferidos",
    "bytes_html",
)


def combinar_janelas(noite: list[dict], dia: list[dict]) -> list[dict]:
    """Uma linha por página. A segunda lista não aumenta o n."""
    if [pagina["id_pagina"] for pagina in noite] != [pagina["id_pagina"] for pagina in dia]:
        raise ValueError("as janelas não têm as mesmas páginas na mesma ordem")
    if not noite:
        raise ValueError("não há páginas para combinar")
    combinadas = []
    for primeira, segunda in zip(noite, dia):
        flags = {}
        instavel = primeira["rubrica_instavel"] or segunda["rubrica_instavel"]
        for item in ITENS_PONTUACAO:
            flags[item] = min(int(primeira[item]), int(segunda[item]))
            instavel = instavel or int(primeira[item]) != int(segunda[item])
        combinada = {
            "id_pagina": primeira["id_pagina"],
            "grupo": primeira["grupo"],
            "rotulo": primeira["rotulo"],
            "url": primeira["url"],
            "tempo_min_ms": min(primeira["tempo_min_ms"], segunda["tempo_min_ms"]),
            "tempo_max_ms": max(primeira["tempo_max_ms"], segunda["tempo_max_ms"]),
            "tempo_noite_ms": primeira["tempo_total_ms"],
            "tempo_dia_ms": segunda["tempo_total_ms"],
            "caches": sorted(set(primeira["caches"]) | set(segunda["caches"])),
            "servidores": sorted(set(primeira["servidores"]) | set(segunda["servidores"])),
            "rubrica_instavel": instavel,
            **flags,
            "pontuacao_seguranca": sum(flags[item] for item in ITENS_PONTUACAO),
            "atende_conjunto_minimo": int(all(flags[item] == 1 for item in ITENS_CONJUNTO_MINIMO)),
        }
        for campo in CAMPOS_MEDIANA:
            combinada[campo] = float(np.median([primeira[campo], segunda[campo]]))
        combinadas.append(combinada)
    return combinadas


def comparar_janelas_pareadas(noite: list[float], dia: list[float], alfa: float = ALFA) -> dict:
    if len(noite) != len(dia) or not noite:
        raise ValueError("as janelas precisam dos mesmos pares")
    diferencas = [float(valor_dia) - float(valor_noite) for valor_noite, valor_dia in zip(noite, dia)]
    mediana = float(np.median(diferencas))
    if all(diferenca == 0 for diferenca in diferencas):
        return {
            "n": len(diferencas),
            "p": 1.0,
            "rejeita": False,
            "metodo": "sem variação entre as janelas",
            "mediana_diferenca": 0.0,
            "estatistica": None,
        }
    resultado = wilcoxon(dia, noite, alternative="two-sided", zero_method="wilcox")
    p_valor = float(resultado.pvalue)
    return {
        "n": len(diferencas),
        "p": p_valor,
        "rejeita": p_valor < alfa,
        "metodo": "Wilcoxon pareado",
        "mediana_diferenca": mediana,
        "estatistica": float(resultado.statistic),
    }


def _ler_janela(janela: str) -> tuple[list[dict], list[dict[str, str]]]:
    relatorio = validar_janela(janela)
    if not relatorio["presente"] or not relatorio["valido"]:
        detalhe = "; ".join(relatorio["problemas"])
        raise SystemExit(f"janela {janela} não está válida para a análise: {detalhe}")
    caminhos = caminhos_s02(janela)
    urls = ler_urls(caminhos["urls"])
    with caminhos["csv"].open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    paginas = agregar_paginas(linhas, [url["id_pagina"] for url in urls])
    return paginas, linhas


def _piloto() -> list[dict]:
    from medicao import caminhos_padrao

    caminhos = caminhos_padrao(PASTA_LAB / "instrumentacao")
    urls = ler_urls(caminhos["urls"])
    with caminhos["csv"].open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    return agregar_paginas(linhas, [url["id_pagina"] for url in urls])


def _mesmo_sinal(confirmatario: dict, piloto: dict) -> str:
    delta_novo = confirmatario["mediana_orgao"] - confirmatario["mediana_portal"]
    delta_velho = piloto["mediana_orgao"] - piloto["mediana_portal"]
    if delta_novo == 0 or delta_velho == 0:
        return "o piloto ou a amostra confirmatória não separou as medianas"
    if (delta_novo > 0) == (delta_velho > 0):
        return "a direção da diferença é a mesma do piloto"
    return "a direção da diferença mudou em relação ao piloto"


def montar_relatorio(
    paginas: list[dict],
    linhas_noite: list[dict[str, str]],
    linhas_dia: list[dict[str, str]],
    piloto: list[dict],
) -> str:
    portal = [pagina for pagina in paginas if pagina["grupo"] == "portal"]
    orgao = [pagina for pagina in paginas if pagina["grupo"] == "orgao"]
    if not portal or not orgao:
        raise ValueError("a amostra precisa dos dois grupos")
    tempo = comparar_grupos([p["tempo_total_ms"] for p in orgao], [p["tempo_total_ms"] for p in portal])
    ttfb = comparar_grupos([p["ttfb_ms"] for p in orgao], [p["ttfb_ms"] for p in portal])
    peso = comparar_grupos(
        [p["bytes_transferidos"] for p in orgao], [p["bytes_transferidos"] for p in portal]
    )
    nota = comparar_grupos(
        [p["pontuacao_seguranca"] for p in orgao], [p["pontuacao_seguranca"] for p in portal]
    )
    horas_pareadas = comparar_janelas_pareadas(
        [p["tempo_noite_ms"] for p in paginas],
        [p["tempo_dia_ms"] for p in paginas],
    )
    piloto_portal = [p for p in piloto if p["grupo"] == "portal"]
    piloto_orgao = [p for p in piloto if p["grupo"] == "orgao"]
    tempo_piloto = comparar_grupos(
        [p["tempo_total_ms"] for p in piloto_orgao], [p["tempo_total_ms"] for p in piloto_portal]
    )
    peso_piloto = comparar_grupos(
        [p["bytes_transferidos"] for p in piloto_orgao], [p["bytes_transferidos"] for p in piloto_portal]
    )
    sucessos = sum(pagina["atende_conjunto_minimo"] for pagina in paginas)
    z_teste = teste_z_proporcao(sucessos, len(paginas))
    exato = teste_binomial(sucessos, len(paginas))
    n_para_queda = tamanho_amostra_proporcao(P0_CONJUNTO_MINIMO, 0.50)
    mediana_tempo_s = float(np.median([pagina["tempo_total_ms"] for pagina in paginas])) / 1000
    mediana_bytes = float(np.median([pagina["bytes_transferidos"] for pagina in paginas]))
    horas = horas_coletivas(PESSOAS_ACESSO_UNICO_MARCO_2026, mediana_tempo_s)
    gib = PESSOAS_ACESSO_UNICO_MARCO_2026 * mediana_bytes / (1024**3)
    resumo_tempo = resumir([pagina["tempo_total_ms"] for pagina in paginas])
    caches = sorted({cache for pagina in paginas for cache in pagina["caches"]})
    instaveis = [pagina["rotulo"] for pagina in paginas if pagina["rubrica_instavel"]]
    decisao_hora = "rejeita H₀" if horas_pareadas["rejeita"] else "não rejeita H₀"
    estatistica_hora = (
        "—"
        if horas_pareadas["estatistica"] is None
        else _fmt(horas_pareadas["estatistica"], 1)
    )
    adequacao = (
        "A aproximação normal do teste Z está confortável para esta conta."
        if z_teste["aproximacao_adequada"]
        else (
            f"n·p₀ = {_fmt(len(paginas) * P0_CONJUNTO_MINIMO, 1)} e "
            f"n·(1−p₀) = {_fmt(len(paginas) * (1 - P0_CONJUNTO_MINIMO), 1)}. "
            "Como um dos dois fica abaixo de 5, a aproximação normal do teste Z não vale para esta amostra. "
            "A leitura segue o teste binomial exato, o mesmo critério do Laboratório 04 e do piloto."
        )
    )
    texto_z = "rejeita H₀" if z_teste["rejeita"] else "não rejeita H₀"
    texto_exato = "rejeita H₀" if exato["rejeita"] else "não rejeita H₀"
    if len(portal) == len(orgao):
        texto_grupos = f"O grupo portal e o grupo órgão têm {len(portal)} páginas cada."
    else:
        texto_grupos = (
            f"O grupo portal tem {len(portal)} páginas e o grupo órgão tem {len(orgao)}. "
            "O desenho não ficou equilibrado; o Mann-Whitney aceita tamanhos diferentes, e o desequilíbrio fica explícito."
        )
    texto_instavel = (
        "A rubrica não foi a mesma em todas as repetições ou entre as janelas em: "
        + ", ".join(instaveis)
        + ". Nesses casos a página ficou com o menor valor."
        if instaveis
        else "A rubrica de segurança foi a mesma nas repetições e nas duas janelas de cada página."
    )
    comparacoes = (
        ("tempo total", tempo),
        ("bytes transferidos", peso),
        ("TTFB", ttfb),
        ("pontuação", nota),
    )
    rejeitam = [nome for nome, resultado in comparacoes if resultado["rejeita"]]
    mantem = [nome for nome, resultado in comparacoes if not resultado["rejeita"]]
    linhas_tabela = []
    for pagina in paginas:
        grupo = "portal" if pagina["grupo"] == "portal" else "órgão"
        linhas_tabela.append(
            f"| {pagina['rotulo']} | {grupo} | {_fmt(pagina['tempo_total_ms'], 0)} | "
            f"{_fmt(pagina['tempo_noite_ms'], 0)} | {_fmt(pagina['tempo_dia_ms'], 0)} | "
            f"{_fmt(pagina['ttfb_ms'], 0)} | {_fmt(pagina['bytes_transferidos'], 0)} | "
            f"{pagina['pontuacao_seguranca']}/8 | {pagina['atende_conjunto_minimo']} | "
            f"{', '.join(pagina['caches'])} |"
        )
    if len(paginas) >= n_para_queda:
        piso = (
            f"A amostra tem {len(paginas)} páginas, acima das cerca de {n_para_queda} que o piloto pediu "
            "para distinguir p = 0,50 de p₀ = 0,80."
        )
    else:
        piso = (
            f"A amostra tem {len(paginas)} páginas. A conta do piloto pedia cerca de {n_para_queda} "
            "para distinguir p = 0,50 de p₀ = 0,80. O piso não foi alcançado."
        )
    if exato["rejeita"] and z_teste["phat"] > P0_CONJUNTO_MINIMO:
        leitura_proporcao = (
            f"{piso} O que apareceu não foi uma queda para 50%: {sucessos} de {len(paginas)} páginas "
            "passaram no conjunto mínimo. O teste exato rejeita p = 0,80 porque a taxa observada ficou "
            f"acima da barra, e o intervalo começa em {_fmt(100 * exato['ic_inferior'], 1)}%, logo acima de 80%. "
            "Isso não mostra falha de cabeçalho. Mostra que, se a taxa fosse exatamente 80%, "
            f"observar {_fmt(100 * z_teste['phat'], 1)}% nesta lista seria pouco comum. "
            "Também não prova que o portal inteiro está nessa taxa."
        )
    elif exato["rejeita"]:
        leitura_proporcao = (
            f"{piso} O teste exato rejeita p = 0,80. A estimativa é "
            f"{sucessos}/{len(paginas)} e o intervalo é "
            f"[{_fmt(100 * exato['ic_inferior'], 1)}%; {_fmt(100 * exato['ic_superior'], 1)}%]."
        )
    else:
        leitura_proporcao = (
            f"{piso} Essa conta era para um efeito grande, de 80% para 50%. "
            "A taxa observada ficou perto de 100% e o teste não rejeitou H₀. "
            "Isso não é falha da coleta: o teste foi desenhado para perceber uma queda, "
            "não para confirmar que todas as páginas passam."
        )
    return f"""# Amostra confirmatória da Sprint 2 — análise

**Responsável:** Walter Louback (análise e impacto)
**Amostra:** {len(paginas)} páginas ({len(portal)} de entrada do portal e {len(orgao)} de órgão), mediana das duas janelas
**Noite:** {_periodo_local(linhas_noite)}
**Dia:** {_periodo_local(linhas_dia)}
**Respostas HTTP:** {len(linhas_noite) + len(linhas_dia)}, três repetições em cada janela
**Plano:** `planejamento/proposta_s01.md`

Este relatório repete as hipóteses da Sprint 1 na amostra maior. Não troca a rubrica e não trata o p-valor como causa.

## 1. Unidade de análise

Cada página entra uma vez. Dentro de uma janela, as três repetições viram uma mediana. Entre as janelas, o número do teste é a mediana dessas duas medianas. As duas janelas não viram duas observações, e as seis respostas não viram seis.

{texto_instavel}

## 2. Descritiva

O tempo da tabela é o que entra no teste, em milissegundos. Noite e dia são as medianas de cada janela, antes de serem combinadas. Bytes são os transferidos com `Accept-Encoding: gzip`.

| Página | Grupo | Tempo no teste | Noite | Dia | TTFB | Bytes | Pontuação | Conjunto mínimo | Cache |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(linhas_tabela)}

Tempo usado no teste: mediana {_fmt(resumo_tempo['mediana'], 0)} ms, mínimo {_fmt(resumo_tempo['minimo'], 0)} ms, máximo {_fmt(resumo_tempo['maximo'], 0)} ms.

Cache observado: {", ".join(caches) or "nenhum"}. O tempo descreve a resposta que este cliente anônimo recebeu, inclusive quando ela veio de cache.

Figuras: `figuras/s02_tempo_total.png`, `figuras/s02_bytes_transferidos.png`, `figuras/s02_pontuacao_seguranca.png`.

## 3. Testes

α = 0,05, testes bicaudais, sem correção para múltiplas comparações. As duas perguntas primárias continuam sendo o tempo total e a proporção do conjunto mínimo. Peso, TTFB e pontuação são secundários. {texto_grupos}

H₀ do tempo, do peso, do TTFB e da pontuação: a distribuição do grupo órgão é igual à do grupo portal. O delta de Cliff é P(órgão > portal) − P(órgão < portal). Limiares de magnitude de Romano et al. (2006): 0,147, 0,33 e 0,474.

| Métrica | Mediana portal | Mediana órgão | Diferença | Teste | U | p | Decisão | Delta de Cliff |
|---|---:|---:|---:|---|---:|---:|---|---|
{_linha_comparacao("Tempo total (ms)", tempo, "ms")}
{_linha_comparacao("TTFB (ms)", ttfb, "ms")}
{_linha_comparacao("Bytes transferidos", peso, "bytes")}
{_linha_comparacao("Pontuação (0–8)", nota, "pontos")}

Nesta lista, rejeitam H₀: {", ".join(rejeitam) or "nenhuma métrica"}. Não rejeitam H₀: {", ".join(mantem) or "nenhuma métrica"}.

No tempo total, {_mesmo_sinal(tempo, tempo_piloto)}. No peso, {_mesmo_sinal(peso, peso_piloto)}. O piloto tinha 4 páginas em cada grupo; esta amostra amplia as duas listas e não repete o mesmo conjunto.

H₀ da proporção, primária: p = 0,80. A barra de 80% continua sendo convenção deste estudo. Não é um SLO do governo.

| Teste | Estimativa | Estatística | p | Decisão |
|---|---:|---:|---:|---|
| Z para uma proporção | {sucessos}/{len(paginas)} = {_fmt(100 * z_teste['phat'], 1)}% | Z = {_fmt(z_teste['z'], 2)} | {_fmt_p(z_teste['p'])} | {texto_z} |
| Binomial exato | {sucessos}/{len(paginas)} = {_fmt(100 * z_teste['phat'], 1)}% | — | {_fmt_p(exato['p'])} | {texto_exato} |

Intervalo exato de 95% para p: [{_fmt(100 * exato['ic_inferior'], 1)}%; {_fmt(100 * exato['ic_superior'], 1)}%].

{adequacao}

{leitura_proporcao}

## 4. As duas janelas

A comparação entre noite e dia não é uma terceira hipótese primária. Ela só pergunta se o horário mudou o tempo da mesma página. O teste é o Wilcoxon pareado, bicaudal, sobre as medianas de cada janela. n = {horas_pareadas['n']} páginas, não {horas_pareadas['n'] * 2}.

| Comparação | Mediana da diferença (dia − noite) | Teste | Estatística | p | Decisão |
|---|---:|---|---:|---:|---|
| Tempo total (ms) | {_fmt(horas_pareadas['mediana_diferenca'], 1)} ms | {horas_pareadas['metodo']} | {estatistica_hora} | {_fmt_p(horas_pareadas['p'])} | {decisao_hora} |

Duas janelas não são uma amostra de horários do dia. Um resultado estável aqui diz que estas duas corridas se pareceram. Não diz que o portal é o mesmo de manhã, de tarde e de madrugada.

## 5. Impacto, em cenário

A fonte pública continua sendo a Agência Gov, via MGI, em 13/04/2026: mais de 80 milhões de pessoas acessaram o GOV.BR em março de 2026. Acesso em 18/11/2026: <https://agenciagov.ebc.com.br/noticias/202604/gov-br-ultrapassa-80-milhoes-de-acessos-unicos-mensais>. O 1,7 bilhão de acessos do trimestre não entra na multiplicação.

Nesta amostra, a mediana do tempo usado no teste foi {_fmt(mediana_tempo_s * 1000, 0)} ms por página, em conexão nova, nesta rede. Para uma pessoa, isso é uma fração de segundo de espera pelo HTML, antes de CSS, JavaScript e imagens.

Cenário, não medição: se cada uma das 80 milhões de pessoas tivesse esperado esse tempo mediano uma única vez, a espera somada seria de {_fmt(horas, 0)} horas. O mesmo cenário, aplicado à mediana de {_fmt(mediana_bytes, 0)} bytes transferidos, soma {_fmt(gib, 1)} GiB. O número coletivo fica grande porque multiplica uma espera pequena por muita gente. Ele não mede o tempo que os cidadãos perderam.

O que esta amostra sustenta, e o que ela não sustenta, está nas ameaças da Sprint 2. Uma diferença entre os grupos medidos não explica a causa. O HTML anônimo destas páginas não descreve o Meu INSS, o Meu SUS Digital nem o uso no celular.

## 6. O que a conta não fecha

- Não há alocação de tratamento. Rejeitar H₀ descreve os grupos medidos.
- A lista não é amostra aleatória dos mais de 13 mil serviços.
- O tempo de HTML em conexão fria não é o tempo da página pronta no navegador.
- Cabeçalho publicado não é vulnerabilidade, e cabeçalho ausente também não.
- Se só o conjunto mínimo virasse meta, um CSP restrito a `frame-ancestors` passaria e a ausência de `script-src` sairia da conta. A pontuação guarda os itens separados por isso.
"""


def executar() -> dict:
    noite, linhas_noite = _ler_janela("noite")
    dia, linhas_dia = _ler_janela("dia")
    paginas = combinar_janelas(noite, dia)
    piloto = _piloto()
    pasta = Path(__file__).resolve().parent / "resultados"
    figuras = pasta / "figuras"
    _grafico(
        paginas,
        "tempo_total_ms",
        "Tempo total do HTML na amostra confirmatória",
        "Milissegundos",
        figuras / "s02_tempo_total.png",
    )
    _grafico(
        paginas,
        "bytes_transferidos",
        "Bytes transferidos na amostra confirmatória",
        "Bytes",
        figuras / "s02_bytes_transferidos.png",
    )
    _grafico(
        paginas,
        "pontuacao_seguranca",
        "Pontuação da rubrica na amostra confirmatória",
        "Pontos",
        figuras / "s02_pontuacao_seguranca.png",
    )
    relatorio = montar_relatorio(paginas, linhas_noite, linhas_dia, piloto)
    destino = pasta / "relatorio_s02.md"
    destino.write_text(relatorio, encoding="utf-8")
    sucessos = int(sum(pagina["atende_conjunto_minimo"] for pagina in paginas))
    resumo = {
        "paginas": len(paginas),
        "portal": sum(pagina["grupo"] == "portal" for pagina in paginas),
        "orgao": sum(pagina["grupo"] == "orgao" for pagina in paginas),
        "respostas": len(linhas_noite) + len(linhas_dia),
        "mediana_tempo_total_ms": float(np.median([pagina["tempo_total_ms"] for pagina in paginas])),
        "mediana_bytes_transferidos": float(np.median([pagina["bytes_transferidos"] for pagina in paginas])),
        "paginas_conjunto_minimo": sucessos,
        "alfa": ALFA,
        "p0_conjunto_minimo": P0_CONJUNTO_MINIMO,
        "janelas": list(JANELAS),
        "nota": "Amostra confirmatória da Sprint 2. Cada página entra uma vez.",
    }
    (pasta / "resumo_s02.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"relatório: {destino}")
    return resumo


if __name__ == "__main__":
    executar()
