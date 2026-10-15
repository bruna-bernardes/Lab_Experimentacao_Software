from pathlib import Path

import pytest

from pipeline.arquivos import ler_csv
from pipeline.exportar import exportar, linhas_releases, url_compare
from tests.fixtures_coleta import FIM, INICIO, detalhes_exemplo, gravar_coleta


def test_exporta_arquivos_esperados(tmp_path):
    config, _ = gravar_coleta(tmp_path)
    resumo = exportar(config)
    saida = Path(config["diretorio_resultados"])

    assert resumo == {"repositorios": 1, "releases": 5, "commits": 5, "runs": 6}
    for nome in ("amostra_final.csv", "releases_janela.csv", "commits_releases.csv.gz",
                 "runs.csv.gz", "funil_selecao.csv"):
        assert (saida / nome).exists(), nome

    amostra = ler_csv(saida / "amostra_final.csv")
    assert [a["repositorio"] for a in amostra] == ["org/repo"]
    assert amostra[0]["ordem_pool"] == "3"


def test_exportacao_deterministica(tmp_path):
    config, _ = gravar_coleta(tmp_path)
    saida = Path(config["diretorio_resultados"])

    exportar(config)
    primeira = {p.name: p.read_bytes() for p in saida.iterdir()}
    exportar(config)
    segunda = {p.name: p.read_bytes() for p in saida.iterdir()}

    assert primeira == segunda


def test_sequencia_de_releases():
    linhas = {l["tag"]: l for l in linhas_releases(detalhes_exemplo(), INICIO, FIM)}

    assert "v0.9.0" not in linhas  # fora da janela
    assert linhas["v1.0.0"]["tag_anterior"] == "v0.9.0"
    assert linhas["v1.0.0"]["primeira_da_historia"] is False
    assert linhas["v1.1.0"]["tag_anterior"] == "v1.0.1"  # pré-release não entra na sequência
    assert linhas["v1.1.0"]["tag_anterior_com_pre"] == "v1.1.0-rc1"
    assert linhas["v1.1.0"]["comparacao_disponivel"] is False
    assert linhas["v1.1.0-rc1"]["prerelease"] is True
    assert "tag_anterior" not in linhas["v1.1.0-rc1"]
    assert linhas["v1.0.1"]["n_commits"] == 1


def test_primeira_release_da_historia():
    detalhes = detalhes_exemplo()
    detalhes["releases_todas"] = detalhes["releases_todas"][1:]

    linhas = {l["tag"]: l for l in linhas_releases(detalhes, INICIO, FIM)}

    assert linhas["v1.0.0"]["primeira_da_historia"] is True


def test_detalhes_da_sprint1_sem_historico_completo():
    detalhes = detalhes_exemplo()
    del detalhes["releases_todas"]

    linhas = {l["tag"]: l for l in linhas_releases(detalhes, INICIO, FIM)}

    assert linhas["v1.0.0"]["tag_anterior"] == "v0.9.0"
    assert linhas["v1.0.0"]["primeira_da_historia"] == ""


def test_url_compare_codifica_tags():
    assert url_compare("o/r", "pkg@1.0.0", "pkg@1.0.1") == \
        "https://github.com/o/r/compare/pkg%401.0.0...pkg%401.0.1"
    assert url_compare("o/r", "", "v1") == ""


def test_sem_coleta(tmp_path):
    with pytest.raises(FileNotFoundError):
        exportar({"inicio": INICIO, "fim": FIM, "diretorio_saida": str(tmp_path),
                  "diretorio_resultados": str(tmp_path / "r")})
