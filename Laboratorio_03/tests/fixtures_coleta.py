"""Fixture compartilhada: uma coleta mínima (progresso + detalhes) em disco."""
import json

from metricas import (
    calcular_cfr_ci, calcular_recuperacao, lead_time_por_commit, lead_time_por_release
)
from pipeline.config import pasta_janela

INICIO = "2026-01-01T00:00:00Z"
FIM = "2026-12-31T23:59:59Z"


def commit(sha, data, mensagem):
    return {"sha": sha, "commit": {"author": {"date": data}, "message": mensagem}}


def run(i, workflow, conclusao, inicio, fim):
    return {"id": i, "workflow_id": workflow, "name": f"wf{workflow}", "conclusion": conclusao,
            "created_at": inicio, "run_started_at": inicio, "updated_at": fim}


def detalhes_exemplo():
    releases_todas = [
        {"tag_name": "v0.9.0", "published_at": "2025-12-01T00:00:00Z", "prerelease": False, "draft": False},
        {"tag_name": "v1.0.0", "published_at": "2026-03-15T00:00:00Z", "prerelease": False, "draft": False},
        {"tag_name": "v1.0.1", "published_at": "2026-03-17T00:00:00Z", "prerelease": False, "draft": False},
        {"tag_name": "v1.1.0-rc1", "published_at": "2026-04-01T00:00:00Z", "prerelease": True, "draft": False},
        {"tag_name": "v1.1.0", "published_at": "2026-05-01T00:00:00Z", "prerelease": False, "draft": False},
        {"tag_name": "v1.2.0", "published_at": "2026-12-29T00:00:00Z", "prerelease": False, "draft": False},
    ]
    comparacoes = [
        {"tag": "v1.0.0", "tag_anterior": "v0.9.0", "published_at": "2026-03-15T00:00:00Z",
         "commits": [commit("a1", "2026-03-02T00:00:00Z", "feat: a\n\ncorpo"),
                     commit("a2", "2026-03-10T00:00:00Z", "feat: b"),
                     commit("a3", "2026-03-14T00:00:00Z", "docs: c")]},
        {"tag": "v1.0.1", "tag_anterior": "v1.0.0", "published_at": "2026-03-17T00:00:00Z",
         "commits": [commit("b1", "2026-03-16T00:00:00Z", "fix: crash ao abrir arquivo")]},
        {"tag": "v1.2.0", "tag_anterior": "v1.1.0", "published_at": "2026-12-29T00:00:00Z",
         "commits": [commit("c1", "2026-12-30T00:00:00Z", "feat: depois da release (rebase)")]},
    ]
    runs = [
        run(1, 10, "success", "2026-01-01T09:00:00Z", "2026-01-01T09:05:00Z"),
        run(2, 10, "failure", "2026-01-01T10:00:00Z", "2026-01-01T10:05:00Z"),
        run(3, 10, "failure", "2026-01-01T10:30:00Z", "2026-01-01T10:35:00Z"),
        run(4, 10, "success", "2026-01-01T11:15:00Z", "2026-01-01T11:20:00Z"),
        run(5, 20, "success", "2026-02-01T09:00:00Z", "2026-02-01T09:05:00Z"),
        run(6, 20, "timed_out", "2026-02-01T10:00:00Z", "2026-02-01T10:05:00Z"),
    ]
    return {"repositorio": "org/repo", "coletado_em": "2026-10-20T00:00:00Z", "branch": "main",
            "releases": [r for r in releases_todas if not r["prerelease"] and r["published_at"] >= INICIO],
            "releases_todas": releases_todas, "comparacoes": comparacoes, "runs": runs,
            "tags": []}


def gravar_coleta(tmp_path):
    config = {"inicio": INICIO, "fim": FIM, "versao_selecao": "selecao_v2", "semente_amostragem": 42,
              "diretorio_saida": str(tmp_path / "dados"),
              "diretorio_resultados": str(tmp_path / "resultados"),
              "diretorio_validacao": str(tmp_path / "validacao"),
              "versao_heuristica": "v1"}
    pasta = pasta_janela(config)
    detalhes = detalhes_exemplo()
    recuperacao = calcular_recuperacao(detalhes["runs"])

    dados = {"repositorio": "org/repo", "branch": "main", "estrelas": 1500, "linguagem": "Python",
             "contribuidores": 12, "idade_dias": 400, "criado_em": "2025-11-26T00:00:00Z",
             "releases": 4, "runs_validas": 6,
             "lead_time_release_horas": lead_time_por_release(detalhes["comparacoes"]),
             "lead_time_commit_horas": lead_time_por_commit(detalhes["comparacoes"]),
             "cfr_ci": calcular_cfr_ci(detalhes["runs"]),
             "recuperacao_horas": recuperacao["mediana_horas"],
             "episodios_censurados": recuperacao["episodios_censurados"],
             "comparacoes_ignoradas": 0,
             "proporcao_censura": recuperacao["proporcao_censura"]}

    for subpasta, conteudo in (
        ("progresso", {"repositorio": "org/repo", "status": "elegivel", "dados": dados, "ordem_pool": 3}),
        ("detalhes", detalhes),
    ):
        (pasta / subpasta).mkdir(parents=True, exist_ok=True)
        (pasta / subpasta / "org__repo.json").write_text(json.dumps(conteudo), encoding="utf-8")

    (pasta / "progresso" / "org__outro.json").write_text(
        json.dumps({"repositorio": "org/outro", "status": "sem_actions"}), encoding="utf-8")
    (pasta / "funil_selecao.csv").write_text("etapa,quantidade\nelegiveis,1\n", encoding="utf-8")
    return config, dados
