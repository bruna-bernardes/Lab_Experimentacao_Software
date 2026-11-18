"""Testes dos cálculos da análise, sem rede e sem o CSV do piloto."""

from __future__ import annotations

import math
import unittest

from analisar_piloto import (
    P0_CONJUNTO_MINIMO,
    agregar_paginas,
    cliffs_delta,
    horas_coletivas,
    tamanho_amostra_proporcao,
    teste_binomial,
    teste_z_proporcao,
)


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


if __name__ == "__main__":
    unittest.main()
