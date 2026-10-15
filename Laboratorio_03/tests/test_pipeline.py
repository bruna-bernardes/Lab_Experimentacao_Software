
import csv
from unittest.mock import patch
from pipeline.__main__ import salvar_csv


def test_salvar_csv_com_bloqueio_temporario(tmp_path):
    caminho = tmp_path / "resultado.csv"
    dados = [{"repositorio": "exemplo/teste"}]

    from os import replace
    chamadas = 0

    def substituir(origem, destino):
        nonlocal chamadas
        chamadas += 1

        if chamadas == 1:
            raise PermissionError("Arquivo temporariamente bloqueado")

        return replace(origem, destino)

    with patch("pipeline.__main__.os.replace", side_effect=substituir), \
         patch("pipeline.__main__.time.sleep") as espera:

        salvar_csv(caminho, dados, ["repositorio"])

    assert chamadas == 2
    espera.assert_called_once_with(1)

    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        registros = list(csv.DictReader(arquivo))

    assert registros == dados


# --- Sprint 2 (#C1) ---------------------------------------------------------
import json
from unittest.mock import Mock

import pipeline.__main__ as principal
from pipeline.__main__ import (
    calcular_funil, executar, processar_repositorio, registrar_erro
)

CONFIG = {
    "inicio": "2026-01-01T00:00:00Z", "fim": "2026-12-31T23:59:59Z",
    "quantidade": 1, "maximo_candidatos": 10, "semente_amostragem": 42,
    "max_tentativas_erro": 2, "coletar_tags": True, "versao_selecao": "selecao_v2",
}


def release(tag, data, pre=False, draft=False):
    return {"tag_name": tag, "published_at": data, "prerelease": pre, "draft": draft}


def releases_validas():
    return [release(f"v1.{i}.0", f"2026-0{i}-01T00:00:00Z") for i in range(1, 7)]


def run(i, conclusao="success"):
    return {"id": i, "workflow_id": 1, "conclusion": conclusao,
            "run_started_at": f"2026-03-01T00:{i % 60:02d}:00Z",
            "updated_at": f"2026-03-01T01:{i % 60:02d}:00Z"}


def test_contribuidores_nao_consultados_para_descartados():
    api = Mock()
    api.paginas.return_value = [release("v1", "2026-02-01T00:00:00Z")]

    with patch.object(principal, "possui_actions", return_value=True), \
         patch.object(principal, "info_repositorio", return_value={"branch": "main"}), \
         patch.object(principal, "contar_contribuidores") as contribuidores, \
         patch.object(principal, "coletar_runs") as runs:
        registro, detalhes = processar_repositorio(api, "org/repo", CONFIG)

    assert registro["status"] == "releases_insuficientes"
    assert detalhes is None
    contribuidores.assert_not_called()
    runs.assert_not_called()


def test_sem_actions_nao_consulta_metadados():
    with patch.object(principal, "possui_actions", return_value=False), \
         patch.object(principal, "info_repositorio") as info:
        registro, _ = processar_repositorio(Mock(), "org/repo", CONFIG)

    assert registro["status"] == "sem_actions"
    info.assert_not_called()


def test_runs_insuficientes():
    api = Mock()
    api.paginas.return_value = releases_validas()

    with patch.object(principal, "possui_actions", return_value=True), \
         patch.object(principal, "info_repositorio", return_value={"branch": "main"}), \
         patch.object(principal, "coletar_runs", return_value=[run(i) for i in range(10)]), \
         patch.object(principal, "contar_contribuidores") as contribuidores:
        registro, _ = processar_repositorio(api, "org/repo", CONFIG)

    assert registro["status"] == "runs_insuficientes"
    contribuidores.assert_not_called()


def test_detalhes_contem_prereleases_e_tags():
    api = Mock()
    api.paginas.return_value = releases_validas() + [
        release("v2.0.0-rc1", "2026-08-01T00:00:00Z", pre=True),
        release("rascunho", "2026-08-02T00:00:00Z", draft=True),
    ]
    runs = [run(i) for i in range(50)] + [run(99, "cancelled")]

    with patch.object(principal, "possui_actions", return_value=True), \
         patch.object(principal, "info_repositorio", return_value={"repositorio": "org/repo", "branch": "main"}), \
         patch.object(principal, "coletar_runs", return_value=runs), \
         patch.object(principal, "contar_contribuidores", return_value=12), \
         patch.object(principal, "coletar_dados_releases", return_value=([], 1)), \
         patch.object(principal, "coletar_tags", return_value=[{"name": "v1.1.0", "commit": {"sha": "abc"}}]):
        registro, detalhes = processar_repositorio(api, "org/repo", CONFIG)

    assert registro["status"] == "elegivel"
    assert registro["dados"]["contribuidores"] == 12
    assert registro["dados"]["releases"] == 6
    assert registro["dados"]["runs_validas"] == 50
    tags = [r["tag_name"] for r in detalhes["releases_todas"]]
    assert "v2.0.0-rc1" in tags and "rascunho" not in tags
    assert detalhes["tags"] == [{"name": "v1.1.0", "sha": "abc"}]


def test_funil_coerente():
    status = ["sem_actions", "sem_actions", "releases_insuficientes", "runs_insuficientes",
              "elegivel", "elegivel", "erro_persistente", "erro"]
    progresso = {f"r{i}": {"repositorio": f"r{i}", "status": s} for i, s in enumerate(status)}

    funil = calcular_funil(progresso, populacao=100)

    assert funil["populacao_busca"] == 100
    assert funil["candidatos_examinados"] == 8
    assert funil["candidatos_examinados"] == (
        funil["sem_actions"] + funil["com_actions"]
        + funil["erros_persistentes"] + funil["erros_pendentes"])
    assert funil["com_actions"] == (
        funil["releases_insuficientes"] + funil["runs_insuficientes"] + funil["elegiveis"])
    assert funil["amostra_final"] == 2


def test_erros_cumulativos_e_persistentes(tmp_path):
    primeiro = registrar_erro(tmp_path, None, "org/repo", "falha 1", max_tentativas=2)
    segundo = registrar_erro(tmp_path, primeiro, "org/repo", "falha 2", max_tentativas=2)

    assert primeiro["status"] == "erro"
    assert segundo["status"] == "erro_persistente"
    erros = json.loads((tmp_path / "erros_coleta.json").read_text(encoding="utf-8"))
    assert [e["erro"] for e in erros] == ["falha 1", "falha 2"]


def test_retomada_nao_reprocessa(tmp_path):
    config = dict(CONFIG, diretorio_saida=str(tmp_path), quantidade=5)
    pool = [{"repositorio": "org/a", "estrelas_busca": 1}, {"repositorio": "org/b", "estrelas_busca": 1}]

    with patch.object(principal, "montar_pool", return_value=pool), \
         patch.object(principal, "processar_repositorio",
                      side_effect=lambda api, nome, cfg: ({"repositorio": nome, "status": "sem_actions"}, None)) as proc:
        executar(config, api=Mock())
        executar(config, api=Mock())

    assert proc.call_count == 2
