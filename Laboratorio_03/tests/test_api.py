
from unittest.mock import Mock, patch
from pipeline.api import GitHubAPI


def test_cache_evitar_requisicoes_repetidas(tmp_path):
    api = GitHubAPI(token="token_teste", cache_dir=tmp_path)

    resposta = Mock()
    resposta.status_code = 200
    resposta.headers = {}
    resposta.json.return_value = {"resultado": "ok"}

    with patch.object(api.session, "get", return_value=resposta) as requisicao:
        primeira = api.get("/repos/exemplo/teste")
        segunda = api.get("/repos/exemplo/teste")

    assert primeira == segunda
    assert requisicao.call_count == 1


def test_cache_persistente(tmp_path):
    api1 = GitHubAPI(token="token_teste", cache_dir=tmp_path)

    resposta = Mock()
    resposta.status_code = 200
    resposta.headers = {}
    resposta.json.return_value = {"resultado": "ok"}

    with patch.object(api1.session, "get", return_value=resposta):
        api1.get("/repos/exemplo/teste")

    api2 = GitHubAPI(token="token_teste", cache_dir=tmp_path)

    with patch.object(api2.session, "get") as requisicao:
        resultado = api2.get("/repos/exemplo/teste")

    assert resultado["data"] == {"resultado": "ok"}
    requisicao.assert_not_called()


def test_rate_limit(tmp_path):
    api = GitHubAPI(token="token_teste", cache_dir=tmp_path)

    bloqueada = Mock()
    bloqueada.status_code = 429
    bloqueada.headers = {"Retry-After": "1"}

    sucesso = Mock()
    sucesso.status_code = 200
    sucesso.headers = {}
    sucesso.json.return_value = {"resultado": "ok"}

    with patch.object(api.session, "get", side_effect=[bloqueada, sucesso]) as requisicao, \
         patch("pipeline.api.time.sleep") as espera:

        resultado = api.get("/repos/exemplo/rate-limit")

    assert resultado["data"] == {"resultado": "ok"}
    assert requisicao.call_count == 2
    espera.assert_called_once_with(1)


def test_erro_temporario_500(tmp_path):
    api = GitHubAPI(token="token_teste", cache_dir=tmp_path)

    erro = Mock()
    erro.status_code = 500
    erro.headers = {}

    sucesso = Mock()
    sucesso.status_code = 200
    sucesso.headers = {}
    sucesso.json.return_value = {"resultado": "ok"}

    with patch.object(api.session, "get", side_effect=[erro, sucesso]) as requisicao, \
         patch("pipeline.api.time.sleep") as espera:

        resultado = api.get("/repos/exemplo/erro-500")

    assert resultado["data"] == {"resultado": "ok"}
    assert requisicao.call_count == 2
    espera.assert_called_once_with(1)
