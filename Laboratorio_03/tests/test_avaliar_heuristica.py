import pytest

from pipeline.arquivos import escrever_csv, ler_csv
from validacao.avaliar_heuristica import avaliar, executar, metricas_binarias, montar_casos


def test_exemplo_numerico_da_especificacao():
    # heurística marcou 40; o consenso confirma 30; o consenso tem 50 corretivas
    reais = [1] * 30 + [0] * 10 + [1] * 20 + [0] * 40
    previstos = [1] * 30 + [1] * 10 + [0] * 20 + [0] * 40

    resultado = metricas_binarias(reais, previstos)

    assert resultado["precisao"] == pytest.approx(0.75)
    assert resultado["recall"] == pytest.approx(0.60)
    assert resultado["f1"] == pytest.approx(2 * 0.75 * 0.6 / 1.35)
    assert (resultado["tp"], resultado["fp"], resultado["fn"], resultado["tn"]) == (30, 10, 20, 40)


def test_sem_positivos_previstos_nao_quebra():
    resultado = metricas_binarias([1, 0], [0, 0])
    assert resultado["precisao"] == 0 and resultado["f1"] == 0


def dados_exemplo():
    consenso = [{"repositorio": "o/r", "tag": "v1.0.1", "corretiva": "sim"},
                {"repositorio": "o/r", "tag": "v1.1.0", "corretiva": "nao"},
                {"repositorio": "o/r", "tag": "v1.1.1", "corretiva": "sim"}]
    releases = [{"repositorio": "o/r", "tag": "v1.0.1", "tag_anterior": "v1.0.0", "url_compare": "u1"},
                {"repositorio": "o/r", "tag": "v1.1.0", "tag_anterior": "v1.0.1", "url_compare": "u2"},
                {"repositorio": "o/r", "tag": "v1.1.1", "tag_anterior": "v1.1.0", "url_compare": "u3"}]
    commits = [{"repositorio": "o/r", "tag": "v1.0.1", "mensagem_primeira_linha": "fix: crash"},
               {"repositorio": "o/r", "tag": "v1.1.0", "mensagem_primeira_linha": "fix: menor"},
               {"repositorio": "o/r", "tag": "v1.1.1", "mensagem_primeira_linha": "chore: deps"}]
    return consenso, releases, commits


def test_avaliacao_e_erros():
    casos = montar_casos(*dados_exemplo())
    resultado, erros = avaliar(casos, "v1")

    assert (resultado["tp"], resultado["fp"], resultado["fn"], resultado["tn"]) == (1, 0, 1, 1)
    assert erros[0]["tag"] == "v1.1.1" and erros[0]["tipo_erro"] == "falso_negativo"


def test_release_ausente():
    consenso, releases, commits = dados_exemplo()
    with pytest.raises(ValueError, match="não estão"):
        montar_casos(consenso, releases[:1], commits)


def test_execucao_reprodutivel_e_uma_linha_por_versao(tmp_path):
    consenso, releases, commits = dados_exemplo()
    escrever_csv(tmp_path / "v" / "consenso_releases.csv", consenso, ["repositorio", "tag", "corretiva"])
    escrever_csv(tmp_path / "r" / "releases_janela.csv", releases, ["repositorio", "tag", "tag_anterior", "url_compare"])
    escrever_csv(tmp_path / "r" / "commits_releases.csv.gz", commits,
                 ["repositorio", "tag", "mensagem_primeira_linha"])

    primeira = executar(["v1", "v3"], tmp_path / "v", tmp_path / "r")
    segunda = executar(["v1"], tmp_path / "v", tmp_path / "r")

    registro = ler_csv(tmp_path / "v" / "heuristica_versoes.csv")
    assert [l["versao"] for l in registro] == ["v1", "v3"]
    assert primeira[0]["f1"] == segunda[0]["f1"]
    assert (tmp_path / "v" / "erros_heuristica_v3.csv").exists()
