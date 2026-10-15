import pytest

from pipeline.arquivos import escrever_csv, ler_csv
from pipeline.consolidar import COLUNAS_DATASET, consolidar
from pipeline.exportar import exportar
from tests.fixtures_coleta import gravar_coleta


def gerar(tmp_path, **extra):
    config, dados_coleta = gravar_coleta(tmp_path)
    config.update(extra)
    exportar(config)
    return config, dados_coleta


def test_regressao_com_valores_da_coleta(tmp_path):
    config, coleta = gerar(tmp_path)
    linha = consolidar(config)[0]

    assert linha["lead_time_release_horas"] == pytest.approx(coleta["lead_time_release_horas"])
    assert linha["lead_time_commit_horas"] == pytest.approx(coleta["lead_time_commit_horas"])
    assert linha["cfr_ci"] == pytest.approx(coleta["cfr_ci"])
    assert linha["recuperacao_horas"] == pytest.approx(coleta["recuperacao_horas"])
    assert linha["episodios_censurados"] == coleta["episodios_censurados"]


def test_metricas_da_sprint2(tmp_path):
    config, _ = gerar(tmp_path)
    linha = consolidar(config)[0]

    assert linha["releases_janela"] == 4
    assert linha["deployment_frequency_semana"] == pytest.approx(4 / (365 / 7), rel=1e-3)
    # v1.0.0 é seguida em 2 dias por v1.0.1 (patch + fix) → falha; v1.2.0 censurada
    assert linha["releases_avaliadas_cfr_entrega"] == 3
    assert linha["releases_falhas_cfr_entrega"] == 1
    assert linha["releases_censuradas_cfr_entrega"] == 1
    assert linha["cfr_entrega"] == pytest.approx(1 / 3)
    assert linha["versao_heuristica"] == "v1"
    assert linha["releases_ignoradas_comparacao"] == 1   # v1.1.0
    assert linha["commits_lead_time_negativo"] == 1      # commit de v1.2.0 após a release
    assert linha["runs_sucesso"] == 3 and linha["runs_falha"] == 3
    assert linha["amostra_ouro"] is False


def test_csv_final_com_colunas_e_consenso(tmp_path):
    config, _ = gerar(tmp_path)
    escrever_csv(tmp_path / "validacao" / "consenso_repositorios.csv",
                 [{"repositorio": "org/repo", "tipo_projeto": "biblioteca_framework", "entregas_reais": "sim"}],
                 ["repositorio", "tipo_projeto", "entregas_reais"])
    consolidar(config)

    linhas = ler_csv(tmp_path / "resultados" / "dataset_final.csv")
    assert list(linhas[0].keys()) == COLUNAS_DATASET
    assert linhas[0]["amostra_ouro"] == "true"
    assert linhas[0]["tipo_projeto_consenso"] == "biblioteca_framework"


def test_versao_da_heuristica_vem_do_config(tmp_path):
    config, _ = gerar(tmp_path, versao_heuristica="v3")

    assert consolidar(config)[0]["versao_heuristica"] == "v3"
