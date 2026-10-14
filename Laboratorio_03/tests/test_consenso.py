import pytest

from pipeline.arquivos import ler_csv
from tests.test_concordancia import escrever
from validacao.comum import AVALIADORES
from validacao.consenso import DecisoesPendentes, calcular, executar, voto_majoritario


def preparar(pasta, tipos_b=("aplicacao_servico",) * 3, corretivas=("sim", "sim", "nao")):
    for avaliador, tipo_b, corretiva in zip(AVALIADORES, tipos_b, corretivas):
        escrever(pasta / "rotulos", avaliador, "repositorios", [
            ("org/a", "biblioteca_framework", "sim"),
            ("org/b", tipo_b, "nao"),
        ])
        escrever(pasta / "rotulos", avaliador, "releases", [("org/a", "v1.0.1", corretiva)])


def test_voto_majoritario():
    assert voto_majoritario(["sim", "sim", "sim"]) == ("sim", "unanime")
    assert voto_majoritario(["sim", "nao", "sim"]) == ("sim", "maioria")
    assert voto_majoritario(["outro", "ferramenta_cli", "aplicacao_servico"]) == (None, "empate")


def test_unanimidade_e_maioria(tmp_path):
    preparar(tmp_path)
    consensos = calcular(tmp_path)

    release = consensos["releases"][0]
    assert release["corretiva"] == "sim" and release["origem_corretiva"] == "maioria"
    repo_a = consensos["repositorios"][0]
    assert repo_a["origem_tipo_projeto"] == "unanime"


def test_empate_sem_decisao_interrompe(tmp_path):
    preparar(tmp_path, tipos_b=("outro", "ferramenta_cli", "aplicacao_servico"))

    with pytest.raises(DecisoesPendentes, match="org/b"):
        calcular(tmp_path)


def test_empate_com_decisao_registrada(tmp_path):
    preparar(tmp_path, tipos_b=("outro", "ferramenta_cli", "aplicacao_servico"))
    (tmp_path / "decisoes_reuniao.csv").write_text(
        "nivel,repositorio,tag,dimensao,rotulo,justificativa,data,presentes\n"
        "repositorios,org/b,,tipo_projeto,ferramenta_cli,README descreve uso pela linha de comando,"
        "2026-11-05,bruna;ana;walter\n", encoding="utf-8")

    executar(tmp_path)
    linhas = ler_csv(tmp_path / "consenso_repositorios.csv")
    repo_b = next(l for l in linhas if l["repositorio"] == "org/b")

    assert repo_b["tipo_projeto"] == "ferramenta_cli"
    assert repo_b["origem_tipo_projeto"] == "reuniao"


def test_decisao_sem_justificativa_e_rejeitada(tmp_path):
    preparar(tmp_path)
    (tmp_path / "decisoes_reuniao.csv").write_text(
        "nivel,repositorio,tag,dimensao,rotulo,justificativa,data,presentes\n"
        "repositorios,org/b,,tipo_projeto,outro,,2026-11-05,todos\n", encoding="utf-8")

    with pytest.raises(ValueError, match="justificativa"):
        calcular(tmp_path)


def test_execucao_cria_modelo_de_decisoes(tmp_path):
    preparar(tmp_path)
    executar(tmp_path)

    assert (tmp_path / "decisoes_reuniao.csv").exists()
    assert len(ler_csv(tmp_path / "consenso_releases.csv")) == 1
