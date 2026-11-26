"""Testes sem rede da instrumentação do Lab 05."""

from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import gzip

from coleta_s02 import janela_congelada
from medicao import (
    COLUNAS,
    ITENS_PONTUACAO,
    Limitador,
    avaliar_cabecalhos,
    caminho_bloqueado,
    decodificar_corpo,
    escrever_csv,
    executar_coleta,
    linha_de_medicao,
)
from validar_piloto import problemas


ROBOTS = """
User-agent: Yandex
Disallow: /ebserh

User-agent: *
Disallow: /economia/pt-br/internet/*
Disallow: /*sendto_form$
Disallow: /*folder_factories$
Disallow: /ebserh
"""


class TestesRobots(unittest.TestCase):
    def test_permite_as_paginas_do_piloto(self):
        for caminho in ("/pt-br", "/pt-br/servicos", "/inss/pt-br", "/mec/pt-br"):
            self.assertFalse(caminho_bloqueado(ROBOTS, caminho), caminho)

    def test_bloqueia_regras_com_curinga_e_prefixo(self):
        self.assertTrue(caminho_bloqueado(ROBOTS, "/ebserh/pt-br"))
        self.assertTrue(caminho_bloqueado(ROBOTS, "/economia/pt-br/internet/noticias"))
        self.assertTrue(caminho_bloqueado(ROBOTS, "/pt-br/alguma/sendto_form"))
        self.assertFalse(caminho_bloqueado(ROBOTS, "/pt-br/servicos"))


class TestesCorpo(unittest.TestCase):
    def test_descompacta_gzip_antes_de_ler_o_robots(self):
        texto = b"User-agent: *\nDisallow: /ebserh\n"
        aberto = decodificar_corpo(gzip.compress(texto), "gzip")
        self.assertIn("user-agent", aberto.decode("utf-8").lower())
        self.assertEqual(decodificar_corpo(texto, ""), texto)


class TestesRubrica(unittest.TestCase):
    def test_conjunto_minimo_sem_tratar_csp_curto_como_completo(self):
        avaliacao = avaliar_cabecalhos(
            {
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Content-Security-Policy": "frame-ancestors 'self';",
                "X-Cache": "HIT",
                "Server": "Zope/exemplo",
            }
        )
        self.assertEqual(avaliacao["atende_conjunto_minimo"], 1)
        self.assertEqual(avaliacao["csp_alem_de_frame"], 0)
        self.assertEqual(avaliacao["permissions_policy"], 0)
        self.assertEqual(avaliacao["hsts_include_subdomains"], 1)
        self.assertEqual(avaliacao["pontuacao_seguranca"], 6)
        self.assertEqual(avaliacao["cache"], "HIT")

    def test_hsts_com_max_age_zero_nao_conta(self):
        avaliacao = avaliar_cabecalhos({"Strict-Transport-Security": "max-age=0"})
        self.assertEqual(avaliacao["hsts"], 0)
        self.assertEqual(avaliacao["atende_conjunto_minimo"], 0)


class RelogioFalso:
    def __init__(self):
        self.agora = 0.0
        self.sonos = []

    def relogio(self):
        return self.agora

    def dormir(self, segundos):
        self.sonos.append(segundos)
        self.agora += segundos


class TestesColeta(unittest.TestCase):
    def test_rodadas_respeitam_o_intervalo_e_gravam_csv(self):
        relogio = RelogioFalso()
        limitador = Limitador(intervalo=1.0, relogio=relogio.relogio, dormir=relogio.dormir)
        urls = [
            {"id_pagina": "a", "grupo": "portal", "rotulo": "A", "url": "https://www.gov.br/pt-br"},
            {"id_pagina": "b", "grupo": "orgao", "rotulo": "B", "url": "https://www.gov.br/inss/pt-br"},
        ]
        chamadas = []

        def robots(limitador):
            limitador.aguardar()
            return 200, "User-agent: *\nDisallow: /ebserh\n"

        def baixar(url, limitador):
            limitador.aguardar()
            chamadas.append(url)
            relogio.agora += 0.2
            return {
                "url_final": url,
                "status_http": 200,
                "redirecionamentos": 0,
                "tempo_tls_ms": 40.0,
                "ttfb_ms": 120.0,
                "tempo_total_ms": 300.0,
                "bytes_transferidos": 1000,
                "bytes_html": 4000,
                "content_encoding": "gzip",
                "erro": "",
                **avaliar_cabecalhos(
                    {
                        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                        "X-Content-Type-Options": "nosniff",
                        "X-Frame-Options": "DENY",
                        "Referrer-Policy": "strict-origin",
                        "Content-Security-Policy": "frame-ancestors 'self'",
                    }
                ),
            }

        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            executar_coleta(
                urls,
                destino_csv=base / "piloto.csv",
                destino_robots=base / "robots.txt",
                destino_meta=base / "meta.json",
                repeticoes=2,
                limitador=limitador,
                obter_robots_fn=robots,
                baixar_fn=baixar,
                mostrar=lambda *_args: None,
            )
            with (base / "piloto.csv").open(encoding="utf-8") as arquivo:
                linhas = list(csv.DictReader(arquivo))
        self.assertEqual([item["id_pagina"] for item in linhas], ["a", "b", "a", "b"])
        self.assertEqual(chamadas, [urls[0]["url"], urls[1]["url"], urls[0]["url"], urls[1]["url"]])
        self.assertGreaterEqual(min(relogio.sonos), 0.79)

    def test_recusa_url_bloqueada_sem_medir_pagina(self):
        urls = [{"id_pagina": "x", "grupo": "portal", "rotulo": "X", "url": "https://www.gov.br/ebserh/pt-br"}]
        baixou = []

        def robots(_limitador):
            return 200, ROBOTS

        def baixar(url, _limitador):
            baixou.append(url)
            return {}

        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            with self.assertRaises(RuntimeError):
                executar_coleta(
                    urls,
                    destino_csv=base / "piloto.csv",
                    destino_robots=base / "robots.txt",
                    destino_meta=base / "meta.json",
                    repeticoes=1,
                    limitador=Limitador(relogio=lambda: 0.0, dormir=lambda _s: None),
                    obter_robots_fn=robots,
                    baixar_fn=baixar,
                )
        self.assertEqual(baixou, [])

    def test_nota_opcional_nao_altera_o_piloto(self):
        urls = [{"id_pagina": "a", "grupo": "portal", "rotulo": "A", "url": "https://www.gov.br/pt-br"}]

        def robots(limitador):
            limitador.aguardar()
            return 200, "User-agent: *\nDisallow:\n"

        def baixar(url, limitador):
            limitador.aguardar()
            return {
                "url_final": url,
                "status_http": 200,
                "redirecionamentos": 0,
                "tempo_tls_ms": 10.0,
                "ttfb_ms": 20.0,
                "tempo_total_ms": 30.0,
                "bytes_transferidos": 100,
                "bytes_html": 200,
                "content_encoding": "identity",
                "erro": "",
                **avaliar_cabecalhos({}),
            }

        relogio = RelogioFalso()
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            meta = executar_coleta(
                urls,
                destino_csv=base / "piloto.csv",
                destino_robots=base / "robots.txt",
                destino_meta=base / "meta.json",
                repeticoes=1,
                limitador=Limitador(relogio=relogio.relogio, dormir=relogio.dormir),
                obter_robots_fn=robots,
                baixar_fn=baixar,
                mostrar=lambda *_args: None,
            )
            self.assertIn("piloto da Sprint 1", meta["nota"])
            relogio_s02 = RelogioFalso()
            meta_s02 = executar_coleta(
                urls,
                destino_csv=base / "s02.csv",
                destino_robots=base / "robots_s02.txt",
                destino_meta=base / "meta_s02.json",
                repeticoes=1,
                limitador=Limitador(relogio=relogio_s02.relogio, dormir=relogio_s02.dormir),
                obter_robots_fn=robots,
                baixar_fn=baixar,
                mostrar=lambda *_args: None,
                nota="Coleta confirmatória da Sprint 2, janela noite.",
            )
        self.assertEqual(meta_s02["nota"], "Coleta confirmatória da Sprint 2, janela noite.")

    def test_janela_com_csv_fica_congelada(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            self.assertFalse(janela_congelada("noite", base))
            destino = base / "dados"
            destino.mkdir()
            (destino / "coleta_s02_noite.csv").write_text("id\n", encoding="utf-8")
            self.assertTrue(janela_congelada("noite", base))
            self.assertFalse(janela_congelada("dia", base))


def _linha_valida(identificador: str, grupo: str, repeticao: int, momento: datetime) -> dict[str, str]:
    medido = {
        "url_final": "https://www.gov.br/pt-br",
        "status_http": 200,
        "redirecionamentos": 0,
        "tempo_tls_ms": 30.0,
        "ttfb_ms": 100.0,
        "tempo_total_ms": 250.0,
        "bytes_transferidos": 800,
        "bytes_html": 2000,
        "content_encoding": "gzip",
        "erro": "",
        **avaliar_cabecalhos(
            {
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "strict-origin",
                "Content-Security-Policy": "frame-ancestors 'self'",
            }
        ),
    }
    linha = linha_de_medicao(
        {"id_pagina": identificador, "grupo": grupo, "rotulo": identificador, "url": "https://www.gov.br/pt-br"},
        repeticao,
        medido,
    )
    linha["coletado_em_utc"] = momento.isoformat(timespec="seconds")
    return linha


class TestesValidacao(unittest.TestCase):
    def test_amostra_sintetica_completa_passa(self):
        urls = [
            {"id_pagina": "p1", "grupo": "portal", "rotulo": "P", "url": "https://www.gov.br/pt-br"},
            {"id_pagina": "o1", "grupo": "orgao", "rotulo": "O", "url": "https://www.gov.br/inss/pt-br"},
        ]
        momento = datetime(2026, 11, 18, 21, 0, tzinfo=timezone.utc)
        linhas = []
        for repeticao in (1, 2, 3):
            for url in urls:
                linhas.append(_linha_valida(url["id_pagina"], url["grupo"], repeticao, momento))
                momento += timedelta(seconds=1.1)
        self.assertEqual(problemas(linhas, urls, "User-agent: *\nDisallow:\n"), [])

    def test_intervalo_curto_e_rubrica_furada_falham(self):
        urls = [{"id_pagina": "p1", "grupo": "portal", "rotulo": "P", "url": "https://www.gov.br/pt-br"}]
        momento = datetime(2026, 11, 18, 21, 0, tzinfo=timezone.utc)
        primeira = _linha_valida("p1", "portal", 1, momento)
        segunda = _linha_valida("p1", "portal", 2, momento + timedelta(milliseconds=200))
        terceira = _linha_valida("p1", "portal", 3, momento + timedelta(seconds=3))
        terceira["atende_conjunto_minimo"] = "1"
        terceira["hsts"] = "0"
        achados = problemas([primeira, segunda, terceira], urls, "User-agent: *\n")
        self.assertTrue(any("intervalo" in item for item in achados))
        self.assertTrue(any("conjunto mínimo" in item for item in achados))
        self.assertTrue(any("pontuação" in item for item in achados))

    def test_contrato_de_colunas_permanece_explicito(self):
        self.assertEqual(len(COLUNAS), 34)
        self.assertEqual(len(ITENS_PONTUACAO), 8)
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "t.csv"
            escrever_csv(caminho, [])
            with caminho.open(encoding="utf-8") as arquivo:
                cabecalho = arquivo.readline().strip().split(",")
        self.assertEqual(tuple(cabecalho), COLUNAS)


if __name__ == "__main__":
    unittest.main()
