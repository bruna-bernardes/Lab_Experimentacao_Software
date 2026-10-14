import pandas as pd
import pytest

from validacao.amostra_ouro import (
    COLUNAS_PLANILHA_RELEASES, COLUNAS_PLANILHA_REPOS, executar, gerar_planilhas,
    sortear_releases, sortear_repositorios
)
from validacao.comum import AVALIADORES, arquivo_rotulos


def amostra(n=80):
    return pd.DataFrame({"repositorio": [f"org/repo{i:03d}" for i in range(n)]})


def releases(repos, por_repo=8):
    linhas = []
    for repo in repos:
        for j in range(por_repo):
            linhas.append({
                "repositorio": repo, "tag": f"v1.{j}.0", "tag_anterior": f"v1.{j - 1}.0" if j else "v0.9.0",
                "published_at": f"2026-0{1 + j % 9}-0{1 + j % 9}T00:00:00Z",
                "prerelease": "true" if j == 7 else "false",
                "comparacao_disponivel": "false" if j == 6 else "true",
                "url_release": f"https://github.com/{repo}/releases/tag/v1.{j}.0",
                "url_compare": f"https://github.com/{repo}/compare/a...b",
            })
    return pd.DataFrame(linhas)


def test_sorteio_reprodutivel_e_independente_da_ordem():
    base = amostra()
    primeiro = sortear_repositorios(base)
    segundo = sortear_repositorios(base.sample(frac=1, random_state=1))

    assert list(primeiro["repositorio"]) == list(segundo["repositorio"])
    assert len(primeiro) == 60
    assert primeiro["repositorio"].is_unique


def test_amostra_pequena_demais():
    with pytest.raises(ValueError):
        sortear_repositorios(amostra(10))


def test_ate_cinco_releases_elegiveis_por_repositorio():
    repos = ["org/a", "org/b"]
    tabela = releases(repos)
    tabela = pd.concat([tabela, releases(["org/c"], por_repo=3)])

    sorteadas = sortear_releases(tabela, repos + ["org/c"])
    por_repo = sorteadas.groupby("repositorio").size().to_dict()

    assert por_repo == {"org/a": 5, "org/b": 5, "org/c": 3}
    assert not sorteadas["tag"].isin(["v1.6.0", "v1.7.0"]).any()  # sem comparação / pré-release
    assert sorteadas.equals(sortear_releases(tabela, repos + ["org/c"]))


def test_planilhas_sem_saida_da_heuristica(tmp_path):
    repos = sortear_repositorios(amostra())
    sorteadas = sortear_releases(releases(list(repos["repositorio"])), list(repos["repositorio"]))

    criados, _ = gerar_planilhas(repos, sorteadas, tmp_path)

    assert len(criados) == 2 * len(AVALIADORES)
    for avaliador in AVALIADORES:
        r = pd.read_csv(arquivo_rotulos(tmp_path, avaliador, "repositorios"), dtype=str, keep_default_na=False)
        s = pd.read_csv(arquivo_rotulos(tmp_path, avaliador, "releases"), dtype=str, keep_default_na=False)
        assert list(r.columns) == COLUNAS_PLANILHA_REPOS
        assert list(s.columns) == COLUNAS_PLANILHA_RELEASES
        assert not any("heur" in c or "previs" in c for c in list(r.columns) + list(s.columns))
        assert (r["tipo_projeto"] == "").all() and (s["corretiva"] == "").all()
        assert r["url_repositorio"].str.startswith("https://github.com/").all()


def test_planilhas_existentes_nao_sao_sobrescritas(tmp_path):
    repos = sortear_repositorios(amostra())
    sorteadas = sortear_releases(releases(list(repos["repositorio"])), list(repos["repositorio"]))
    gerar_planilhas(repos, sorteadas, tmp_path)

    destino = arquivo_rotulos(tmp_path, "ana", "repositorios")
    destino.write_text("rotulado à mão", encoding="utf-8")
    criados, preservados = gerar_planilhas(repos, sorteadas, tmp_path)

    assert criados == []
    assert destino in preservados
    assert destino.read_text(encoding="utf-8") == "rotulado à mão"


def test_execucao_completa(tmp_path):
    (tmp_path / "resultados").mkdir()
    base = amostra()
    base.to_csv(tmp_path / "resultados" / "amostra_final.csv", index=False)
    releases(list(base["repositorio"])).to_csv(tmp_path / "resultados" / "releases_janela.csv", index=False)

    executar(tmp_path / "resultados", tmp_path / "validacao")
    primeira = (tmp_path / "validacao" / "amostra_ouro_releases.csv").read_bytes()
    executar(tmp_path / "resultados", tmp_path / "validacao")

    assert (tmp_path / "validacao" / "amostra_ouro_releases.csv").read_bytes() == primeira
    assert len(pd.read_csv(tmp_path / "validacao" / "amostra_ouro_repositorios.csv")) == 60
