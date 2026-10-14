import pytest

from heuristica import (
    apenas_patch, eh_corretiva, eh_mensagem_correcao, fracao_correcao,
    mensagens_indicam_correcao, parse_versao, VERSOES
)


def test_exemplos_da_especificacao():
    assert eh_corretiva("v2.3.0", "v2.3.1", ["fix: crash ao abrir arquivo"]) is True
    assert eh_corretiva("v2.4.0", "v2.5.0", ["feat: nova tela"]) is False


@pytest.mark.parametrize("tag, esperado", [
    ("v1.2.3", ("", (1, 2, 3))),
    ("1.2.3", ("", (1, 2, 3))),
    ("release-1.2.3", ("release", (1, 2, 3))),
    ("pkg@1.2.3", ("pkg", (1, 2, 3))),
    ("pkg@v1.2.3", ("pkg", (1, 2, 3))),
    ("v1.2", ("", (1, 2, 0))),
    ("v1.2.3.4", ("", (1, 2, 3, 4))),
    ("v1.2.3-beta.1", ("", (1, 2, 3))),
    ("2026.01.05", None),
    ("nightly", None),
    ("", None),
])
def test_parse_versao(tag, esperado):
    assert parse_versao(tag) == esperado


def test_apenas_patch():
    assert apenas_patch("v1.2.3", "v1.2.4") is True
    assert apenas_patch("v1.2.3", "v1.3.0") is False
    assert apenas_patch("v1.2.3", "v2.0.0") is False
    assert apenas_patch("v1.2.3", "v1.2.3") is False
    assert apenas_patch("v1.2.3.1", "v1.2.3.2") is True
    assert apenas_patch("v1.2", "v1.2.1") is True
    assert apenas_patch("a@1.0.0", "b@1.0.1") is False
    assert apenas_patch("2026.01.01", "2026.01.02") is None


@pytest.mark.parametrize("mensagem, esperado", [
    ("fix: crash", True),
    ("fix(parser): erro", True),
    ("Fixes #123", True),
    ("fixed typo", True),
    ("hotfix para produção", True),
    ("hot-fix", True),
    ("bugfix", True),
    ('Revert "feat: x"', True),
    ("add prefix option", False),
    ("suffix handling", False),
    ("fixture update", False),
    ("feat: nova tela", False),
    ("", False),
    (None, False),
])
def test_mensagem_de_correcao(mensagem, esperado):
    assert eh_mensagem_correcao(mensagem) is esperado


def test_lista_vazia_de_mensagens():
    assert mensagens_indicam_correcao([]) is False
    assert mensagens_indicam_correcao(None) is False
    assert fracao_correcao([]) == 0.0
    assert eh_corretiva("v1.0.0", "v1.0.1", []) is False


def test_sem_semver_usa_mensagens():
    assert eh_corretiva("2026.01.01", "2026.01.02", ["fix: x"]) is True
    assert eh_corretiva("2026.01.01", "2026.01.02", ["feat: x"]) is False


def test_sem_release_anterior():
    assert eh_corretiva(None, "v1.0.1", ["fix: x"]) is False


def test_versao_desconhecida():
    with pytest.raises(ValueError):
        eh_corretiva("v1.0.0", "v1.0.1", [], versao="v99")


def test_versoes_candidatas():
    mensagens = ["fix: a", "feat: b", "docs: c"]

    assert VERSOES["v1"]("v1.0.0", "v1.0.1", mensagens) is True
    assert VERSOES["v2"]("v1.0.0", "v1.0.1", mensagens) is False
    assert VERSOES["v2"]("v1.0.0", "v1.0.1", ["fix: a", "fix: b", "docs"]) is True
    assert VERSOES["v3"]("v1.0.0", "v1.0.1", ["feat: x"]) is True
    assert VERSOES["v3"]("x", "y", ["fix: a"]) is True
    assert VERSOES["v2"]("x", "y", ["fix: a"]) is True
    assert VERSOES["v1"]("a@1.0.0", "b@1.0.1", ["fix"]) is False
