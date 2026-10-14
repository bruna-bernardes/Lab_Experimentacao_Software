import pytest

from metricas import calcular_cfr_entrega, deployment_frequency

INICIO = "2026-01-01T00:00:00Z"
FIM = "2026-12-31T23:59:59Z"


def rel(tag, data, corretiva=False):
    return {"tag_name": tag, "published_at": f"{data}T00:00:00Z", "corretiva": corretiva}


def classificar(anterior, atual):
    return atual["corretiva"]


def test_deployment_frequency():
    assert deployment_frequency(52, "2026-01-01T00:00:00Z", "2026-12-31T00:00:00Z") == pytest.approx(1.0)
    assert deployment_frequency(0, INICIO, FIM) == 0
    assert deployment_frequency(365, "2025-10-01T00:00:00Z", "2026-10-01T00:00:00Z") == pytest.approx(7.0)


def test_deployment_frequency_janela_invalida():
    with pytest.raises(ValueError):
        deployment_frequency(5, FIM, INICIO)


def test_exemplo_da_especificacao():
    releases = [
        rel("v2.3.0", "2026-05-10"),
        rel("v2.3.1", "2026-05-12", corretiva=True),
        rel("v2.4.0", "2026-06-01"),
        rel("v2.5.0", "2026-06-20"),
    ]

    resultado = calcular_cfr_entrega(releases, classificar, INICIO, FIM)

    assert resultado == {"cfr": 1 / 4, "avaliadas": 4, "falhas": 1, "censuradas": 0}


def test_releases_nos_ultimos_7_dias_sao_censuradas():
    releases = [rel("v1.0.0", "2026-06-01"), rel("v1.0.1", "2026-12-28", corretiva=True)]

    resultado = calcular_cfr_entrega(releases, classificar, INICIO, FIM)

    assert resultado["censuradas"] == 1
    assert resultado["avaliadas"] == 1
    assert resultado["falhas"] == 0


def test_corretiva_fora_do_prazo_nao_conta():
    releases = [rel("v1.0.0", "2026-03-01"), rel("v1.0.1", "2026-03-09", corretiva=True)]

    assert calcular_cfr_entrega(releases, classificar, INICIO, FIM)["falhas"] == 0


def test_corretiva_exatamente_em_7_dias_conta():
    releases = [rel("v1.0.0", "2026-03-01"), rel("v1.0.1", "2026-03-08", corretiva=True)]

    assert calcular_cfr_entrega(releases, classificar, INICIO, FIM)["falhas"] == 1


def test_unica_release():
    resultado = calcular_cfr_entrega([rel("v1.0.0", "2026-03-01")], classificar, INICIO, FIM)

    assert resultado == {"cfr": 0.0, "avaliadas": 1, "falhas": 0, "censuradas": 0}


def test_lista_vazia():
    assert calcular_cfr_entrega([], classificar, INICIO, FIM)["cfr"] is None


def test_release_anterior_a_janela_nao_entra_mas_conta_como_vizinha():
    releases = [rel("v1.0.0", "2025-12-30"), rel("v1.0.1", "2026-01-02", corretiva=True),
                rel("v1.1.0", "2026-02-01")]

    resultado = calcular_cfr_entrega(releases, classificar, INICIO, FIM)

    assert resultado["avaliadas"] == 2
    assert resultado["falhas"] == 0


def test_ordem_de_entrada_nao_importa():
    releases = [rel("v1.0.1", "2026-03-03", corretiva=True), rel("v1.0.0", "2026-03-01")]

    assert calcular_cfr_entrega(releases, classificar, INICIO, FIM)["falhas"] == 1
