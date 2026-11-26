"""Testes dos cálculos da análise, sem rede e sem o CSV do piloto."""

from __future__ import annotations

import math
import unittest
from datetime import datetime, timedelta, timezone

from analisar_piloto import (
    P0_CONJUNTO_MINIMO,
    agregar_paginas,
    cliffs_delta,
    horas_coletivas,
    tamanho_amostra_proporcao,
    teste_binomial,
    teste_z_proporcao,
)
from analisar_s02 import combinar_janelas, comparar_janelas_pareadas, montar_relatorio


class TestesEfeito(unittest.TestCase):
    def test_delta_de_cliff_nos_extremos(self):
        self.assertEqual(cliffs_delta([1, 2, 3], [1, 2, 3]), 0)
        self.assertEqual(cliffs_delta([2, 3, 4], [1, 2, 3]), 5 / 9)
        self.assertEqual(cliffs_delta([1, 1], [2, 2]), -1)

    def test_z_sob_a_hipotese_nula_e_no_caso_do_piloto_cheio(self):
        nulo = teste_z_proporcao(50, 100, p0=0.5)
        self.assertAlmostEqual(nulo["z"], 0.0)
        self.assertAlmostEqual(nulo["p"], 1.0)
        cheio = teste_z_proporcao(8, 8, p0=0.8)
        self.assertAlmostEqual(cheio["z"], 0.2 / math.sqrt(0.16 / 8))
        self.assertFalse(cheio["aproximacao_adequada"])
        self.assertFalse(cheio["rejeita"])

    def test_binomial_exato_concorda_com_a_direcao_do_z_quando_todos_passam(self):
        exato = teste_binomial(8, 8, p0=P0_CONJUNTO_MINIMO)
        self.assertFalse(exato["rejeita"])
        self.assertLess(exato["ic_inferior"], 1)
        self.assertEqual(exato["ic_superior"], 1)

    def test_tamanho_de_amostra_e_cenario_de_horas(self):
        self.assertGreaterEqual(tamanho_amostra_proporcao(0.80, 0.50), 15)
        self.assertLessEqual(tamanho_amostra_proporcao(0.80, 0.50), 20)
        self.assertAlmostEqual(horas_coletivas(80_000_000, 0.5), 80_000_000 * 0.5 / 3600)


class TestesAgregacao(unittest.TestCase):
    def test_mediana_e_rubrica_conservadora(self):
        def linha(repeticao, tempo, hsts):
            return {
                "id_pagina": "p",
                "grupo": "portal",
                "rotulo": "Página",
                "url_solicitada": "https://www.gov.br/pt-br",
                "status_http": "200",
                "erro": "",
                "tempo_total_ms": str(tempo),
                "ttfb_ms": "100",
                "tempo_tls_ms": "40",
                "bytes_transferidos": "1000",
                "bytes_html": "3000",
                "cache": "HIT",
                "servidor": "Zope",
                "hsts": str(hsts),
                "hsts_include_subdomains": "1",
                "nosniff": "1",
                "clickjacking": "1",
                "referrer_policy": "1",
                "csp": "1",
                "csp_alem_de_frame": "0",
                "permissions_policy": "0",
            }

        paginas = agregar_paginas(
            [linha(1, 100, 1), linha(2, 300, 1), linha(3, 200, 0)],
            ["p"],
        )
        self.assertEqual(paginas[0]["tempo_total_ms"], 200)
        self.assertEqual(paginas[0]["hsts"], 0)
        self.assertEqual(paginas[0]["atende_conjunto_minimo"], 0)
        self.assertTrue(paginas[0]["rubrica_instavel"])
        self.assertEqual(paginas[0]["pontuacao_seguranca"], 5)


def _repeticoes(identificador: str, grupo: str, tempos: tuple[int, int, int], hsts: int) -> list[dict[str, str]]:
    linhas = []
    for repeticao, tempo in enumerate(tempos, start=1):
        linhas.append(
            {
                "id_pagina": identificador,
                "grupo": grupo,
                "rotulo": identificador,
                "url_solicitada": f"https://www.gov.br/{identificador}",
                "status_http": "200",
                "erro": "",
                "tempo_total_ms": str(tempo),
                "ttfb_ms": "100",
                "tempo_tls_ms": "40",
                "bytes_transferidos": "1000",
                "bytes_html": "3000",
                "cache": "HIT",
                "servidor": "Zope",
                "hsts": str(hsts),
                "hsts_include_subdomains": "1",
                "nosniff": "1",
                "clickjacking": "1",
                "referrer_policy": "1",
                "csp": "1",
                "csp_alem_de_frame": "0",
                "permissions_policy": "0",
            }
        )
    return linhas


class TestesDuasJanelas(unittest.TestCase):
    def _janela(self, deslocamento: int, hsts_portal: int) -> list[dict]:
        linhas = []
        linhas.extend(_repeticoes("p1", "portal", (100 + deslocamento, 120 + deslocamento, 140 + deslocamento), hsts_portal))
        linhas.extend(_repeticoes("p2", "portal", (160 + deslocamento, 180 + deslocamento, 200 + deslocamento), 1))
        linhas.extend(_repeticoes("o1", "orgao", (220 + deslocamento, 240 + deslocamento, 260 + deslocamento), 1))
        linhas.extend(_repeticoes("o2", "orgao", (280 + deslocamento, 300 + deslocamento, 320 + deslocamento), 1))
        return agregar_paginas(linhas, ["p1", "p2", "o1", "o2"])

    def test_duas_janelas_nao_dobram_o_n(self):
        noite = self._janela(0, 1)
        dia = self._janela(80, 0)
        combinadas = combinar_janelas(noite, dia)
        self.assertEqual(len(combinadas), 4)
        self.assertEqual(combinadas[0]["tempo_noite_ms"], 120)
        self.assertEqual(combinadas[0]["tempo_dia_ms"], 200)
        self.assertEqual(combinadas[0]["tempo_total_ms"], 160)
        self.assertEqual(combinadas[0]["hsts"], 0)
        self.assertTrue(combinadas[0]["rubrica_instavel"])
        self.assertEqual(combinadas[0]["atende_conjunto_minimo"], 0)

    def test_wilcoxon_percebe_a_janela_mais_lenta_e_o_empate(self):
        mudou = comparar_janelas_pareadas(
            [100, 110, 120, 130, 140, 150],
            [180, 190, 200, 210, 220, 230],
        )
        self.assertTrue(mudou["rejeita"])
        self.assertEqual(mudou["n"], 6)
        self.assertGreater(mudou["mediana_diferenca"], 0)
        empate = comparar_janelas_pareadas([10, 20], [10, 20])
        self.assertFalse(empate["rejeita"])
        self.assertEqual(empate["mediana_diferenca"], 0)
        self.assertIn("sem variação", empate["metodo"])

    def test_relatorio_fala_em_paginas_e_nao_em_requisicoes(self):
        noite = self._janela(0, 1)
        dia = self._janela(0, 1)
        paginas = combinar_janelas(noite, dia)
        inicio = datetime(2026, 11, 26, 2, 0, tzinfo=timezone.utc)
        linhas = [
            {"coletado_em_utc": (inicio + timedelta(seconds=indice)).isoformat()}
            for indice in range(12)
        ]
        texto = montar_relatorio(paginas, linhas, linhas, noite)
        self.assertIn("4 páginas", texto)
        self.assertIn("As duas janelas não viram duas observações", texto)
        self.assertNotIn("n = 8", texto)


if __name__ == "__main__":
    unittest.main()
