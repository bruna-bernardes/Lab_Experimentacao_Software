"""Teste de integração de ponta a ponta da Sprint 2, offline e com dados
sintéticos: exportar → consolidar → sorteio da amostra-ouro → rótulos →
kappa de Fleiss → consenso → avaliação da heurística → dataset com consenso."""
import json

import pandas as pd

from pipeline.arquivos import ler_csv
from pipeline.config import pasta_janela
from pipeline.consolidar import consolidar
from pipeline.exportar import exportar
from validacao import amostra_ouro, avaliar_heuristica, concordancia, consenso
from validacao.comum import AVALIADORES, arquivo_rotulos

INICIO, FIM = "2026-01-01T00:00:00Z", "2026-12-31T23:59:59Z"


def coleta_sintetica(tmp_path, n=65):
    config = {"inicio": INICIO, "fim": FIM, "versao_selecao": "selecao_v2", "semente_amostragem": 42,
              "diretorio_saida": str(tmp_path / "dados"), "diretorio_resultados": str(tmp_path / "resultados"),
              "diretorio_validacao": str(tmp_path / "validacao"), "versao_heuristica": "v1"}
    pasta = pasta_janela(config)
    (pasta / "progresso").mkdir(parents=True)
    (pasta / "detalhes").mkdir(parents=True)

    for i in range(n):
        nome = f"org/repo{i:03d}"
        tags = ["v0.9.0"] + [f"v1.{j // 2}.{j % 2}" for j in range(8)]
        datas = ["2025-12-01"] + [f"2026-{1 + j:02d}-{10 + (j % 2) * 3:02d}" for j in range(8)]
        todas = [{"tag_name": t, "published_at": f"{d}T00:00:00Z", "prerelease": False, "draft": False}
                 for t, d in zip(tags, datas)]
        comparacoes = [{
            "tag": tags[k], "tag_anterior": tags[k - 1], "published_at": todas[k]["published_at"],
            "commits": [{"sha": f"{i}-{k}", "commit": {
                "author": {"date": f"{datas[k][:8]}01T00:00:00Z"},
                "message": "fix: bug" if tags[k].endswith(".1") else "feat: algo"}}],
        } for k in range(1, len(tags))]
        runs = [{"id": r, "workflow_id": 1, "name": "ci", "conclusion": "failure" if r % 5 == 0 else "success",
                 "created_at": f"2026-03-01T{r % 24:02d}:00:00Z",
                 "run_started_at": f"2026-03-{1 + r // 24:02d}T{r % 24:02d}:00:00Z",
                 "updated_at": f"2026-03-{1 + r // 24:02d}T{r % 24:02d}:30:00Z"} for r in range(60)]
        detalhes = {"repositorio": nome, "coletado_em": "2026-10-20T00:00:00Z", "branch": "main",
                    "releases": todas[1:], "releases_todas": todas, "comparacoes": comparacoes, "runs": runs}
        dados = {"repositorio": nome, "branch": "main", "estrelas": 1000 + i, "linguagem": "Go",
                 "contribuidores": 5, "idade_dias": 300, "criado_em": "2025-01-01T00:00:00Z"}
        arquivo = nome.replace("/", "__") + ".json"
        (pasta / "detalhes" / arquivo).write_text(json.dumps(detalhes), encoding="utf-8")
        (pasta / "progresso" / arquivo).write_text(json.dumps(
            {"repositorio": nome, "status": "elegivel", "dados": dados, "ordem_pool": i + 1}), encoding="utf-8")
    return config


def rotular(validacao):
    """Simula os três avaliadores: concordam em quase tudo, com uma divergência
    2-1 e um empate 1-1-1 resolvido em reunião."""
    tipos = ["biblioteca_framework", "aplicacao_servico", "ferramenta_cli"]
    for indice, avaliador in enumerate(AVALIADORES):
        repos = pd.read_csv(arquivo_rotulos(validacao / "rotulos", avaliador, "repositorios"),
                            dtype=str, keep_default_na=False)
        repos["tipo_projeto"] = "biblioteca_framework"
        repos["entregas_reais"] = "sim"
        repos.loc[0, "tipo_projeto"] = tipos[indice]           # empate 1-1-1
        if indice == 2:
            repos.loc[1, "entregas_reais"] = "incerto"         # divergência 2-1
        repos.to_csv(arquivo_rotulos(validacao / "rotulos", avaliador, "repositorios"), index=False)

        releases = pd.read_csv(arquivo_rotulos(validacao / "rotulos", avaliador, "releases"),
                               dtype=str, keep_default_na=False)
        releases["corretiva"] = ["sim" if t.endswith(".1") else "nao" for t in releases["tag"]]
        releases.to_csv(arquivo_rotulos(validacao / "rotulos", avaliador, "releases"), index=False)

    primeiro = pd.read_csv(arquivo_rotulos(validacao / "rotulos", "bruna", "repositorios"))["repositorio"][0]
    (validacao / "decisoes_reuniao.csv").write_text(
        "nivel,repositorio,tag,dimensao,rotulo,justificativa,data,presentes\n"
        f"repositorios,{primeiro},,tipo_projeto,biblioteca_framework,publica pacote no PyPI,2026-11-05,todos\n",
        encoding="utf-8")


def test_fluxo_completo_da_sprint2(tmp_path):
    config = coleta_sintetica(tmp_path)
    resultados, validacao = tmp_path / "resultados", tmp_path / "validacao"

    assert exportar(config)["repositorios"] == 65
    assert len(consolidar(config)) == 65

    repos, releases = amostra_ouro.executar(resultados, validacao)
    assert len(repos) == 60 and len(releases) == 60 * 5

    rotular(validacao)
    resultados_kappa, divergencias = concordancia.executar(validacao)
    kappas = {r["dimensao"]: r for r in resultados_kappa}
    assert kappas["corretiva"]["kappa_fleiss"] == 1.0
    assert len(divergencias) == 2

    consenso.executar(validacao)
    avaliacao = avaliar_heuristica.executar(["v1"], validacao, resultados)[0]
    assert avaliacao["f1"] == 1.0

    dataset = consolidar(config)
    assert sum(linha["amostra_ouro"] for linha in dataset) == 60
    linha = ler_csv(resultados / "dataset_final.csv")[0]
    assert linha["cfr_entrega"] != "" and linha["deployment_frequency_semana"] != ""
