import numpy as np
import pytest
from statsmodels.stats.inter_rater import fleiss_kappa

from validacao.comum import AVALIADORES, arquivo_rotulos
from validacao.concordancia import (
    RotulosInvalidos, calcular, carregar_nivel, concordancia_bruta, executar,
    interpretar_kappa, kappa_fleiss, padrao
)


def escrever(pasta, avaliador, nivel, linhas):
    pasta.mkdir(parents=True, exist_ok=True)
    if nivel == "repositorios":
        cabecalho = "repositorio,url_repositorio,tipo_projeto,entregas_reais,observacoes"
        corpo = [f"{r},https://github.com/{r},{t},{e}," for r, t, e in linhas]
    else:
        cabecalho = "repositorio,tag,tag_anterior,url_release,url_compare,corretiva,observacoes"
        corpo = [f"{r},{tag},,,,{c}," for r, tag, c in linhas]
    arquivo_rotulos(pasta, avaliador, nivel).write_text("\n".join([cabecalho] + corpo) + "\n", encoding="utf-8")


def rotulos_validos(pasta, divergir=False):
    for i, avaliador in enumerate(AVALIADORES):
        tipo_b = "ferramenta_cli" if (divergir and i == 2) else "aplicacao_servico"
        escrever(pasta, avaliador, "repositorios", [
            ("org/a", "biblioteca_framework", "sim"),
            ("org/b", tipo_b, "nao"),
            ("org/c", "outro", "incerto"),
        ])
        escrever(pasta, avaliador, "releases", [
            ("org/a", "v1.0.1", "sim"), ("org/a", "v1.1.0", "nao"), ("org/b", "v2.0.1", "sim"),
        ])


def test_tabela_classica_de_fleiss():
    # Fleiss (1971), exemplo usado na Wikipedia: 10 sujeitos, 14 avaliadores, 5 categorias.
    tabela = np.array([[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0],
                       [2, 2, 8, 1, 1], [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2],
                       [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]])
    assert fleiss_kappa(tabela, method="fleiss") == pytest.approx(0.210, abs=1e-3)


def test_concordancia_perfeita(tmp_path):
    rotulos_validos(tmp_path)
    resultados, divergencias = calcular(tmp_path)

    kappas = {r["dimensao"]: r["kappa_fleiss"] for r in resultados}
    assert kappas == {"tipo_projeto": 1.0, "entregas_reais": 1.0, "corretiva": 1.0}
    assert divergencias == []


def test_divergencias_listadas(tmp_path):
    rotulos_validos(tmp_path, divergir=True)
    resultados, divergencias = calcular(tmp_path)

    assert len(divergencias) == 1
    assert divergencias[0]["repositorio"] == "org/b"
    assert divergencias[0]["padrao"] == "2-1"
    assert divergencias[0]["rotulo_walter"] == "ferramenta_cli"
    tipo = next(r for r in resultados if r["dimensao"] == "tipo_projeto")
    assert tipo["kappa_fleiss"] < 1


def test_kappa_indefinido_quando_so_ha_uma_categoria():
    assert kappa_fleiss([["sim"] * 3, ["sim"] * 3]) is None
    assert interpretar_kappa(None) == "indefinido"


@pytest.mark.parametrize("kappa, esperado", [
    (-0.1, "pobre"), (0.0, "leve"), (0.20, "leve"), (0.21, "razoavel"), (0.40, "razoavel"),
    (0.41, "moderada"), (0.60, "moderada"), (0.61, "substancial"), (0.80, "substancial"),
    (0.81, "quase perfeita"), (1.0, "quase perfeita"),
])
def test_faixas_landis_koch(kappa, esperado):
    assert interpretar_kappa(kappa) == esperado


def test_concordancia_bruta_e_padrao():
    unanime, pares = concordancia_bruta([["a", "a", "a"], ["a", "a", "b"]])
    assert unanime == 0.5
    assert pares == pytest.approx(4 / 6)
    assert padrao(["a", "b", "c"]) == "1-1-1"


def test_valor_fora_do_vocabulario(tmp_path):
    rotulos_validos(tmp_path)
    escrever(tmp_path, "ana", "releases", [("org/a", "v1.0.1", "talvez"), ("org/a", "v1.1.0", "nao"),
                                          ("org/b", "v2.0.1", "sim")])
    with pytest.raises(RotulosInvalidos, match="talvez"):
        carregar_nivel(tmp_path, "releases")


def test_celula_vazia_e_item_faltando(tmp_path):
    rotulos_validos(tmp_path)
    escrever(tmp_path, "walter", "repositorios", [("org/a", "", "sim"), ("org/b", "outro", "nao")])
    with pytest.raises(RotulosInvalidos) as erro:
        carregar_nivel(tmp_path, "repositorios")
    assert "vazio" in str(erro.value) and "faltam 1" in str(erro.value)


def test_arquivo_ausente(tmp_path):
    with pytest.raises(RotulosInvalidos, match="não encontrado"):
        carregar_nivel(tmp_path, "repositorios")


def test_planilha_salva_pelo_excel(tmp_path):
    rotulos_validos(tmp_path)
    texto = ("repositorio;url_repositorio;tipo_projeto;entregas_reais;observacoes\n"
             "org/a;x;Biblioteca_Framework;Sim;ação\norg/b;x;aplicacao_servico;Não;\norg/c;x;outro;incerto;\n")
    arquivo_rotulos(tmp_path, "bruna", "repositorios").write_bytes(texto.encode("cp1252"))

    rotulos = carregar_nivel(tmp_path, "repositorios")
    assert rotulos["bruna"][("org/a",)]["tipo_projeto"] == "biblioteca_framework"
    assert rotulos["bruna"][("org/b",)]["entregas_reais"] == "nao"


def test_execucao_gera_arquivos(tmp_path):
    rotulos_validos(tmp_path / "rotulos", divergir=True)
    executar(tmp_path)

    assert (tmp_path / "concordancia.csv").exists()
    assert (tmp_path / "divergencias.csv").exists()
