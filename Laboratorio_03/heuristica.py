"""Heurística de identificação de releases corretivas (RQ 03 b).

Uma release corretiva é aquela cujo objetivo principal é corrigir um defeito
recente. A heurística olha para a mudança de versão (SemVer) entre a release
anterior e a atual e para as mensagens dos commits incluídos na release atual.

Versões registradas (todas continuam executáveis para comparação na avaliação):

- ``v1`` (pré-registrada): a versão muda apenas no *patch* **e** há ao menos um
  commit com ``fix``, ``hotfix``, ``bugfix`` ou ``revert``. Se uma das tags não
  segue SemVer, decide apenas pelas mensagens.
- ``v2`` (candidata): muda apenas o *patch* **e** pelo menos metade dos commits
  são de correção ("objetivo principal"). Sem SemVer, só a fração de commits.
- ``v3`` (candidata): muda apenas o *patch*, independentemente das mensagens.
  Sem SemVer, decide pelas mensagens, como a v1.

As versões v2 e v3 foram definidas antes da avaliação. Novas versões criadas
após a avaliação devem ser acrescentadas a ``VERSOES`` sem apagar as antigas.
"""
import re

PADRAO_VERSAO = re.compile(r"^(?P<prefixo>.*?)(?P<numeros>\d+(?:\.\d+){1,3})(?P<sufixo>[-+._].*)?$")

PADRAO_CORRECAO = re.compile(
    r"(?<![a-z0-9])(fix(es|ed)?|hot-?fix(es)?|bug-?fix(es)?|revert(s|ed)?)(?![a-z0-9])",
    re.IGNORECASE
)

ANO_MINIMO_CALVER = 1900


def normalizar_prefixo(prefixo):
    prefixo = prefixo.strip().lower()
    prefixo = re.sub(r"v$", "", prefixo)
    return prefixo.rstrip("-_/@ .")


def parse_versao(tag):
    """``(prefixo, (major, minor, patch[, build]))`` ou ``None`` quando a tag
    não segue SemVer. Versões por data (ex.: ``2026.01.05``) devolvem ``None``."""
    if not tag:
        return None

    encontrado = PADRAO_VERSAO.match(tag.strip())
    if not encontrado:
        return None

    numeros = tuple(int(n) for n in encontrado.group("numeros").split("."))
    if numeros[0] >= ANO_MINIMO_CALVER:
        return None

    if len(numeros) == 2:
        numeros = numeros + (0,)

    return normalizar_prefixo(encontrado.group("prefixo")), numeros


def apenas_patch(tag_anterior, tag_atual):
    """Verdadeiro se major e minor são iguais e só o patch (ou um componente
    posterior) aumentou. ``None`` se alguma tag não for SemVer. Prefixos
    diferentes (pacotes diferentes num monorepo) devolvem ``False``."""
    anterior, atual = parse_versao(tag_anterior), parse_versao(tag_atual)

    if anterior is None or atual is None:
        return None

    (prefixo_a, versao_a), (prefixo_b, versao_b) = anterior, atual
    if prefixo_a != prefixo_b:
        return False

    if versao_a[:2] != versao_b[:2]:
        return False

    resto_a = versao_a[2:] + (0,) * (len(versao_b) - len(versao_a))
    resto_b = versao_b[2:] + (0,) * (len(versao_a) - len(versao_b))
    return resto_b > resto_a


def eh_mensagem_correcao(mensagem):
    return bool(mensagem) and bool(PADRAO_CORRECAO.search(mensagem))


def mensagens_indicam_correcao(mensagens):
    return any(eh_mensagem_correcao(m) for m in mensagens or [])


def fracao_correcao(mensagens):
    mensagens = list(mensagens or [])
    if not mensagens:
        return 0.0
    return sum(eh_mensagem_correcao(m) for m in mensagens) / len(mensagens)


def regra_v1(tag_anterior, tag_atual, mensagens):
    patch = apenas_patch(tag_anterior, tag_atual)
    correcao = mensagens_indicam_correcao(mensagens)
    if patch is None:
        return correcao
    return patch and correcao


def regra_v2(tag_anterior, tag_atual, mensagens):
    patch = apenas_patch(tag_anterior, tag_atual)
    maioria = fracao_correcao(mensagens) >= 0.5
    if patch is None:
        return maioria
    return patch and maioria


def regra_v3(tag_anterior, tag_atual, mensagens):
    patch = apenas_patch(tag_anterior, tag_atual)
    if patch is None:
        return mensagens_indicam_correcao(mensagens)
    return patch


VERSOES = {
    "v1": regra_v1,
    "v2": regra_v2,
    "v3": regra_v3,
}

DESCRICOES = {
    "v1": "apenas patch E ao menos um commit fix/hotfix/bugfix/revert (sem SemVer: só mensagens)",
    "v2": "apenas patch E >= 50% dos commits de correção (sem SemVer: só a fração)",
    "v3": "apenas patch (sem SemVer: ao menos um commit de correção)",
}


def eh_corretiva(tag_anterior, tag_atual, mensagens, versao="v1"):
    if versao not in VERSOES:
        raise ValueError(f"Versão de heurística desconhecida: {versao}. Opções: {sorted(VERSOES)}")
    if not tag_anterior:
        return False
    return bool(VERSOES[versao](tag_anterior, tag_atual, mensagens))
