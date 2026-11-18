"""Análise do piloto da Sprint 1.

Responsável: Walter Louback (análise e impacto).

Lê o CSV validado, agrega as três repetições de cada página e aplica o
plano declarado em planejamento/proposta_s01.md. Os p-valores deste
arquivo descrevem o piloto; a amostra confirmatória é a da Sprint 2.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from scipy.stats import binomtest, mannwhitneyu, norm

PASTA_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PASTA_LAB / "instrumentacao"))

from medicao import ITENS_CONJUNTO_MINIMO, ITENS_PONTUACAO, caminhos_padrao, ler_urls
from validar_piloto import problemas

ALFA = 0.05
P0_CONJUNTO_MINIMO = 0.80
PESSOAS_ACESSO_UNICO_MARCO_2026 = 80_000_000
COR_PORTAL = "#1B4F72"
COR_ORGAO = "#B9770E"


def cliffs_delta(referencia: list[float], comparacao: list[float]) -> float:
    """P(referência > comparação) − P(referência < comparação)."""
    maior = menor = 0
    for valor in referencia:
        for outro in comparacao:
            if valor > outro:
                maior += 1
            elif valor < outro:
                menor += 1
    total = len(referencia) * len(comparacao)
    if total == 0:
        raise ValueError("amostras vazias")
    return (maior - menor) / total


def rotulo_cliff(delta: float) -> str:
    magnitude = abs(delta)
    if magnitude < 0.147:
        return "desprezível"
    if magnitude < 0.33:
        return "pequeno"
    if magnitude < 0.474:
        return "médio"
    return "grande"


def teste_z_proporcao(sucessos: int, n: int, p0: float = P0_CONJUNTO_MINIMO, alfa: float = ALFA) -> dict:
    if n <= 0 or not 0 < p0 < 1:
        raise ValueError("n positivo e 0 < p0 < 1 são necessários")
    phat = sucessos / n
    z = (phat - p0) / math.sqrt(p0 * (1 - p0) / n)
    p_valor = float(2 * norm.sf(abs(z)))
    return {
        "sucessos": sucessos,
        "n": n,
        "phat": phat,
        "p0": p0,
        "z": z,
        "p": p_valor,
        "rejeita": p_valor < alfa,
        "aproximacao_adequada": n * p0 >= 5 and n * (1 - p0) >= 5,
    }


def teste_binomial(sucessos: int, n: int, p0: float = P0_CONJUNTO_MINIMO, alfa: float = ALFA) -> dict:
    resultado = binomtest(sucessos, n, p=p0, alternative="two-sided")
    intervalo = resultado.proportion_ci(confidence_level=1 - alfa, method="exact")
    return {
        "sucessos": sucessos,
        "n": n,
        "p0": p0,
        "p": float(resultado.pvalue),
        "rejeita": float(resultado.pvalue) < alfa,
        "ic_inferior": float(intervalo.low),
        "ic_superior": float(intervalo.high),
    }


def comparar_grupos(orgao: list[float], portal: list[float], alfa: float = ALFA) -> dict:
    try:
        resultado = mannwhitneyu(orgao, portal, alternative="two-sided", method="exact")
        metodo = "exato"
    except ValueError:
        resultado = mannwhitneyu(orgao, portal, alternative="two-sided", method="asymptotic")
        metodo = "assintótico"
    delta = cliffs_delta(orgao, portal)
    return {
        "u": float(resultado.statistic),
        "p": float(resultado.pvalue),
        "metodo": metodo,
        "rejeita": float(resultado.pvalue) < alfa,
        "delta_cliff": delta,
        "magnitude": rotulo_cliff(delta),
        "mediana_orgao": float(np.median(orgao)),
        "mediana_portal": float(np.median(portal)),
        "n_orgao": len(orgao),
        "n_portal": len(portal),
    }


def tamanho_amostra_proporcao(p0: float, p1: float, alfa: float = ALFA, poder: float = 0.80) -> int:
    if p0 == p1 or not 0 < p0 < 1 or not 0 < p1 < 1:
        raise ValueError("p0 e p1 precisam estar entre 0 e 1 e ser diferentes")
    z_alfa = norm.ppf(1 - alfa / 2)
    z_poder = norm.ppf(poder)
    numerador = z_alfa * math.sqrt(p0 * (1 - p0)) + z_poder * math.sqrt(p1 * (1 - p1))
    return int(math.ceil((numerador / (p1 - p0)) ** 2))


def horas_coletivas(pessoas: int, segundos: float) -> float:
    return pessoas * segundos / 3600


def resumir(valores: list[float]) -> dict:
    amostra = np.asarray(valores, dtype=float)
    return {
        "n": int(amostra.size),
        "minimo": float(amostra.min()),
        "q1": float(np.percentile(amostra, 25)),
        "mediana": float(np.median(amostra)),
        "media": float(amostra.mean()),
        "q3": float(np.percentile(amostra, 75)),
        "maximo": float(amostra.max()),
        "desvio": float(amostra.std(ddof=1)) if amostra.size > 1 else 0.0,
    }


def agregar_paginas(linhas: list[dict[str, str]], ordem: list[str]) -> list[dict]:
    por_pagina: dict[str, list[dict[str, str]]] = defaultdict(list)
    for linha in linhas:
        por_pagina[linha["id_pagina"]].append(linha)
    paginas = []
    for identificador in ordem:
        repeticoes = por_pagina[identificador]
        validas = [linha for linha in repeticoes if not linha["erro"] and linha["status_http"] == "200"]
        if len(validas) != len(repeticoes) or not validas:
            raise ValueError(f"página sem três respostas válidas: {identificador}")
        base = validas[0]

        def mediana(coluna: str) -> float:
            return float(np.median([float(linha[coluna]) for linha in validas]))

        flags = {}
        instavel = False
        for item in ITENS_PONTUACAO:
            valores = [int(linha[item]) for linha in validas]
            instavel = instavel or len(set(valores)) > 1
            flags[item] = min(valores)
        tempos = [float(linha["tempo_total_ms"]) for linha in validas]
        paginas.append(
            {
                "id_pagina": identificador,
                "grupo": base["grupo"],
                "rotulo": base["rotulo"],
                "url": base["url_solicitada"],
                "tempo_total_ms": mediana("tempo_total_ms"),
                "tempo_min_ms": min(tempos),
                "tempo_max_ms": max(tempos),
                "ttfb_ms": mediana("ttfb_ms"),
                "tempo_tls_ms": mediana("tempo_tls_ms"),
                "bytes_transferidos": mediana("bytes_transferidos"),
                "bytes_html": mediana("bytes_html"),
                "caches": sorted({linha["cache"] for linha in validas}),
                "servidores": sorted({linha["servidor"] for linha in validas}),
                "rubrica_instavel": instavel,
                **flags,
                "pontuacao_seguranca": sum(flags[item] for item in ITENS_PONTUACAO),
                "atende_conjunto_minimo": int(all(flags[item] == 1 for item in ITENS_CONJUNTO_MINIMO)),
            }
        )
    return paginas


def _fmt(valor: float, casas: int = 1) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_p(valor: float) -> str:
    if valor < 0.0001:
        return f"{valor:.2e}".replace(".", ",")
    return f"{valor:.4f}".replace(".", ",")


def _grafico(paginas: list[dict], coluna: str, titulo: str, eixo: str, caminho: Path) -> None:
    fig, eixo_y = plt.subplots(figsize=(9.2, 4.8))
    posicoes = np.arange(len(paginas))
    cores = [COR_PORTAL if pagina["grupo"] == "portal" else COR_ORGAO for pagina in paginas]
    eixo_y.barh(posicoes, [pagina[coluna] for pagina in paginas], color=cores)
    eixo_y.set_yticks(posicoes, [pagina["rotulo"] for pagina in paginas])
    eixo_y.invert_yaxis()
    eixo_y.set_xlabel(eixo)
    eixo_y.set_title(titulo)
    eixo_y.legend(
        handles=[
            Patch(facecolor=COR_PORTAL, label="Entrada do portal"),
            Patch(facecolor=COR_ORGAO, label="Página inicial de órgão"),
        ]
    )
    fig.tight_layout()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=120)
    plt.close(fig)


def _linha_comparacao(nome: str, resultado: dict, unidade: str) -> str:
    diferenca = resultado["mediana_orgao"] - resultado["mediana_portal"]
    decisao = "rejeita H₀" if resultado["rejeita"] else "não rejeita H₀"
    return (
        f"| {nome} | {_fmt(resultado['mediana_portal'], 1)} | {_fmt(resultado['mediana_orgao'], 1)} | "
        f"{_fmt(diferenca, 1)} {unidade} | {resultado['metodo']} | {_fmt(resultado['u'], 1)} | "
        f"{_fmt_p(resultado['p'])} | {decisao} | {_fmt(resultado['delta_cliff'], 2)} ({resultado['magnitude']}) |"
    )


def _periodo_local(linhas: list[dict[str, str]]) -> str:
    momentos = [datetime.fromisoformat(linha["coletado_em_utc"]) for linha in linhas]
    fuso = ZoneInfo("America/Sao_Paulo")
    inicio = min(momentos).astimezone(fuso)
    fim = max(momentos).astimezone(fuso)
    return f"{inicio.strftime('%d/%m/%Y %H:%M')}–{fim.strftime('%H:%M')} (horário de Brasília)"


def montar_relatorio(paginas: list[dict], linhas: list[dict[str, str]]) -> str:
    portal = [pagina for pagina in paginas if pagina["grupo"] == "portal"]
    orgao = [pagina for pagina in paginas if pagina["grupo"] == "orgao"]
    tempo = comparar_grupos([p["tempo_total_ms"] for p in orgao], [p["tempo_total_ms"] for p in portal])
    ttfb = comparar_grupos([p["ttfb_ms"] for p in orgao], [p["ttfb_ms"] for p in portal])
    peso = comparar_grupos(
        [p["bytes_transferidos"] for p in orgao], [p["bytes_transferidos"] for p in portal]
    )
    nota = comparar_grupos(
        [p["pontuacao_seguranca"] for p in orgao], [p["pontuacao_seguranca"] for p in portal]
    )
    sucessos = sum(pagina["atende_conjunto_minimo"] for pagina in paginas)
    z_teste = teste_z_proporcao(sucessos, len(paginas))
    exato = teste_binomial(sucessos, len(paginas))
    n_para_queda = tamanho_amostra_proporcao(P0_CONJUNTO_MINIMO, 0.50)
    mediana_tempo_s = float(np.median([pagina["tempo_total_ms"] for pagina in paginas])) / 1000
    mediana_bytes = float(np.median([pagina["bytes_transferidos"] for pagina in paginas]))
    horas = horas_coletivas(PESSOAS_ACESSO_UNICO_MARCO_2026, mediana_tempo_s)
    gib = PESSOAS_ACESSO_UNICO_MARCO_2026 * mediana_bytes / (1024**3)
    caches = sorted({cache for pagina in paginas for cache in pagina["caches"]})
    banners = sorted({servidor for pagina in paginas for servidor in pagina["servidores"] if servidor})
    sem_banner = [pagina["rotulo"] for pagina in paginas if not any(pagina["servidores"])]
    instaveis = [pagina["rotulo"] for pagina in paginas if pagina["rubrica_instavel"]]

    linhas_tabela = []
    for pagina in paginas:
        grupo = "portal" if pagina["grupo"] == "portal" else "órgão"
        linhas_tabela.append(
            f"| {pagina['rotulo']} | {grupo} | {_fmt(pagina['tempo_total_ms'], 0)} | "
            f"{_fmt(pagina['tempo_min_ms'], 0)}–{_fmt(pagina['tempo_max_ms'], 0)} | "
            f"{_fmt(pagina['ttfb_ms'], 0)} | {_fmt(pagina['bytes_transferidos'], 0)} | "
            f"{pagina['pontuacao_seguranca']}/8 | {pagina['atende_conjunto_minimo']} | {', '.join(pagina['caches'])} |"
        )

    adequacao = (
        "A aproximação normal do teste Z está confortável para esta conta."
        if z_teste["aproximacao_adequada"]
        else (
            f"n·p₀ = {_fmt(len(paginas) * P0_CONJUNTO_MINIMO, 1)} e "
            f"n·(1−p₀) = {_fmt(len(paginas) * (1 - P0_CONJUNTO_MINIMO), 1)}. "
            "Como n·(1−p₀) fica abaixo de 5, a aproximação normal do teste Z não vale para esta amostra. "
            "A leitura do piloto segue o teste binomial exato, o mesmo critério praticado no Laboratório 04."
        )
    )
    texto_z = "rejeita H₀" if z_teste["rejeita"] else "não rejeita H₀"
    texto_exato = "rejeita H₀" if exato["rejeita"] else "não rejeita H₀"
    texto_instavel = (
        "A rubrica variou entre repetições em: " + ", ".join(instaveis) + ". Nesses casos a página ficou com o menor valor."
        if instaveis
        else "A rubrica de segurança foi a mesma nas três repetições de cada página."
    )
    if banners and not sem_banner:
        texto_servidor = f"Cabeçalho `Server` em todas as páginas: {'; '.join(banners)}."
    elif banners:
        texto_servidor = (
            f"Cabeçalho `Server` em {len(paginas) - len(sem_banner)} das {len(paginas)} páginas: "
            f"{'; '.join(banners)}. Ausente em {', '.join(sem_banner)}."
        )
    else:
        texto_servidor = "Nenhuma página trouxe o cabeçalho `Server`."
    comparacoes = (
        ("tempo total", tempo),
        ("bytes transferidos", peso),
        ("TTFB", ttfb),
        ("pontuação", nota),
    )
    rejeitam = [nome for nome, resultado in comparacoes if resultado["rejeita"]]
    mantem = [nome for nome, resultado in comparacoes if not resultado["rejeita"]]
    texto_separacao = (
        f"Nesta lista, rejeitam H₀: {', '.join(rejeitam) or 'nenhuma métrica'}. "
        f"Não rejeitam H₀: {', '.join(mantem) or 'nenhuma métrica'}. "
        "Isso descreve as oito páginas. A amostra da Sprint 2 é que repete a pergunta."
    )

    return f"""# Piloto da Sprint 1 — análise

**Responsável:** Walter Louback (análise e impacto)
**Amostra:** {len(paginas)} páginas, mediana de 3 repetições cada ({len(linhas)} respostas HTTP)
**Quando:** {_periodo_local(linhas)}
**Plano:** `planejamento/proposta_s01.md`

Este relatório descreve o piloto. Ele testa o instrumento e mostra a ordem de grandeza das medidas. A conclusão do estudo fica para a amostra da Sprint 2.

## 1. Unidade de análise

Cada página entra uma vez. As três repetições estimam o ruído da medição; a unidade dos testes é a mediana delas. Tratar as 24 respostas como observações independentes inflaria a amostra.

{texto_instavel}

## 2. Descritiva

Mediana das três repetições. Tempos em milissegundos. Bytes são os transferidos com `Accept-Encoding: gzip`.

| Página | Grupo | Tempo total | Mín.–máx. das repetições | TTFB | Bytes | Pontuação | Conjunto mínimo | Cache |
|---|---|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(linhas_tabela)}

Tempo total, nas medianas das páginas: mediana {_fmt(resumir([p['tempo_total_ms'] for p in paginas])['mediana'], 0)} ms, mínimo {_fmt(resumir([p['tempo_total_ms'] for p in paginas])['minimo'], 0)} ms, máximo {_fmt(resumir([p['tempo_total_ms'] for p in paginas])['maximo'], 0)} ms.

Cache observado: {", ".join(caches)}. O tempo descreve a resposta que este cliente anônimo recebeu, inclusive quando ela veio de cache.

{texto_servidor} O banner identifica a pilha anunciada pela resposta; não é uma auditoria do ambiente.

Figuras: `figuras/tempo_total.png`, `figuras/bytes_transferidos.png`, `figuras/pontuacao_seguranca.png`.

## 3. Testes do piloto

α = 0,05, testes bicaudais, sem correção para múltiplas comparações. O piloto não decide o estudo. As duas perguntas primárias declaradas no plano são o tempo total e a proporção do conjunto mínimo. Peso, TTFB e pontuação são secundários.

H₀ do tempo, do peso, do TTFB e da pontuação: a distribuição do grupo órgão é igual à do grupo portal. O delta de Cliff é P(órgão > portal) − P(órgão < portal). Limiares de magnitude de Romano et al. (2006): 0,147, 0,33 e 0,474.

| Métrica | Mediana portal | Mediana órgão | Diferença | Teste | U | p | Decisão | Delta de Cliff |
|---|---:|---:|---:|---|---:|---:|---|---|
{_linha_comparacao("Tempo total (ms)", tempo, "ms")}
{_linha_comparacao("TTFB (ms)", ttfb, "ms")}
{_linha_comparacao("Bytes transferidos", peso, "bytes")}
{_linha_comparacao("Pontuação (0–8)", nota, "pontos")}

{texto_separacao}

H₀ da proporção, primária: p = 0,80. A barra de 80% é convenção deste estudo, no mesmo espírito da meta de 5% do Laboratório 04. Não é um SLO publicado pelo governo.

| Teste | Estimativa | Estatística | p | Decisão |
|---|---:|---:|---:|---|
| Z para uma proporção | {sucessos}/{len(paginas)} = {_fmt(100 * z_teste['phat'], 1)}% | Z = {_fmt(z_teste['z'], 2)} | {_fmt_p(z_teste['p'])} | {texto_z} |
| Binomial exato | {sucessos}/{len(paginas)} = {_fmt(100 * z_teste['phat'], 1)}% | — | {_fmt_p(exato['p'])} | {texto_exato} |

Intervalo exato de 95% para p: [{_fmt(100 * exato['ic_inferior'], 1)}%; {_fmt(100 * exato['ic_superior'], 1)}%].

{adequacao}

Com {len(paginas)} páginas, o intervalo ainda é largo. Uma taxa de 100% nesta amostra convive com valores bem mais baixos no intervalo. Para ter cerca de 80% de poder para distinguir p = 0,50 de p₀ = 0,80, no teste bicaudal com α = 0,05, a conta normal pede cerca de {n_para_queda} páginas. A Sprint 2 precisa passar desse tamanho. Oito páginas servem para ensaiar o instrumento.

## 4. Impacto, em cenário

A fonte pública usada aqui é a Agência Gov, via MGI, em 13/04/2026: mais de 80 milhões de pessoas acessaram o GOV.BR em março de 2026, e o trimestre janeiro–março teve 1,7 bilhão de acessos. Acesso em 18/11/2026: <https://agenciagov.ebc.com.br/noticias/202604/gov-br-ultrapassa-80-milhoes-de-acessos-unicos-mensais>.

No piloto, a mediana do tempo total do HTML foi {_fmt(mediana_tempo_s * 1000, 0)} ms por página, em conexão nova, nesta rede. Para uma pessoa, isso é uma fração de segundo de espera pelo HTML, antes de CSS, JavaScript e imagens.

Cenário, não medição: se cada uma das 80 milhões de pessoas — o piso publicado para março — tivesse esperado esse tempo mediano uma única vez, a espera somada seria de {_fmt(horas, 0)} horas. O mesmo cenário, aplicado à mediana de {_fmt(mediana_bytes, 0)} bytes transferidos, soma {_fmt(gib, 1)} GiB. O número coletivo fica grande porque multiplica uma espera pequena por muita gente. Ele não mede o tempo que os cidadãos perderam.

O trimestre de 1,7 bilhão de acessos não entra nessa conta. Aqueles acessos misturam páginas, aplicativos, sessões autenticadas e cache em outras redes. Multiplicá-los por este HTML inflaria o impacto sem uma definição de acesso que a gente tenha medido.

O que o piloto sustenta, se a amostra maior repetir o padrão: a política de cabeçalhos destas páginas é propriedade da plataforma, não de cada órgão, e o peso do HTML varia entre as páginas. Uma espera de algumas centenas de milissegundos no HTML anônimo não descreve o Meu INSS, o Meu SUS Digital nem o uso no celular.

## 5. O que esta análise não fecha

- Não há alocação de tratamento. Um p-valor pequeno indicaria diferença entre os grupos medidos, não a causa dela.
- Oito páginas e uma rede, num único horário, não representam os mais de 13 mil serviços nem os aplicativos.
- O tempo de HTML em conexão fria não é o tempo da página pronta no navegador.
- O conjunto mínimo e a pontuação observam cabeçalhos publicados. Não medem vulnerabilidade.
- A Lei de Goodhart cabe no desenho: se só o conjunto mínimo virasse meta, um CSP restrito a `frame-ancestors` passaria e a ausência de `script-src` sumiria da conta. Por isso a pontuação guarda os itens separados.
"""


def executar() -> dict:
    caminhos = caminhos_padrao(PASTA_LAB / "instrumentacao")
    urls = ler_urls(caminhos["urls"])
    with caminhos["csv"].open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    texto_robots = caminhos["robots"].read_text(encoding="utf-8")
    achados = problemas(linhas, urls, texto_robots)
    if achados:
        raise SystemExit("piloto inválido:\n- " + "\n- ".join(achados))

    paginas = agregar_paginas(linhas, [url["id_pagina"] for url in urls])
    pasta = Path(__file__).resolve().parent / "resultados"
    figuras = pasta / "figuras"
    _grafico(paginas, "tempo_total_ms", "Tempo total do HTML (mediana das repetições)", "Milissegundos", figuras / "tempo_total.png")
    _grafico(
        paginas,
        "bytes_transferidos",
        "Bytes transferidos (mediana das repetições)",
        "Bytes",
        figuras / "bytes_transferidos.png",
    )
    _grafico(
        paginas,
        "pontuacao_seguranca",
        "Pontuação da rubrica de cabeçalhos (0 a 8)",
        "Pontos",
        figuras / "pontuacao_seguranca.png",
    )
    relatorio = montar_relatorio(paginas, linhas)
    destino = pasta / "relatorio_piloto.md"
    destino.write_text(relatorio, encoding="utf-8")
    resumo = {
        "paginas": len(paginas),
        "respostas": len(linhas),
        "mediana_tempo_total_ms": float(np.median([pagina["tempo_total_ms"] for pagina in paginas])),
        "mediana_bytes_transferidos": float(np.median([pagina["bytes_transferidos"] for pagina in paginas])),
        "paginas_conjunto_minimo": int(sum(pagina["atende_conjunto_minimo"] for pagina in paginas)),
        "alfa": ALFA,
        "p0_conjunto_minimo": P0_CONJUNTO_MINIMO,
        "nota": "Resultados do piloto. A amostra confirmatória é a da Sprint 2.",
    }
    (pasta / "resumo_piloto.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"relatório: {destino}")
    return resumo


if __name__ == "__main__":
    executar()
