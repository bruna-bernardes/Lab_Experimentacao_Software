from pathlib import Path

from pipeline.arquivos import ler_csv
from pipeline.dicionario import ESQUEMAS, gerar_markdown, verificar

DICIONARIO = Path(__file__).resolve().parents[1] / "resultados" / "dicionario_dados.csv"


def test_dicionario_cobre_todas_as_colunas_geradas():
    problemas = list(verificar(ler_csv(DICIONARIO)))
    assert problemas == [], "\n".join(problemas)


def test_verificacao_detecta_coluna_nao_documentada():
    dicionario = [l for l in ler_csv(DICIONARIO) if l["campo"] != "cfr_entrega"]
    assert any("cfr_entrega" in p for p in verificar(dicionario))


def test_verificacao_detecta_campo_inexistente_e_incompleto():
    dicionario = ler_csv(DICIONARIO) + [
        {"arquivo": "resultados/dataset_final.csv", "campo": "fantasma", "tipo": "x",
         "unidade": "x", "origem": "x", "formula": "x"},
        {"arquivo": "resultados/runs.csv.gz", "campo": "run_id", "tipo": "", "unidade": "",
         "origem": "", "formula": ""},
    ]
    problemas = list(verificar(dicionario))
    assert any("fantasma" in p for p in problemas)
    assert any("campos vazios" in p for p in problemas)


def test_markdown_tem_uma_secao_por_arquivo():
    texto = gerar_markdown(ler_csv(DICIONARIO))
    for arquivo in ESQUEMAS:
        assert f"`{arquivo}`" in texto
