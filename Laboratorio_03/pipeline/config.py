"""Leitura da configuração e localização das pastas de saída do pipeline."""
import hashlib
import json
from pathlib import Path

PADROES = {
    "quantidade": 320,
    "maximo_candidatos": 6000,
    "semente_amostragem": 42,
    "max_tentativas_erro": 3,
    "coletar_tags": True,
    "versao_selecao": "selecao_v2",
    "versao_heuristica": "v1",
    "diretorio_saida": "dados",
    "diretorio_resultados": "resultados",
    "diretorio_validacao": "validacao",
    "cache_dir": ".cache/github",
}


def carregar_config(caminho="config.json"):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

    for chave in ("inicio", "fim"):
        if chave not in config:
            raise ValueError(f"Configuração sem o campo obrigatório '{chave}'.")

    return {**PADROES, **config}


def chave_janela(config):
    """Identifica a combinação janela + estratégia de seleção. Mudar qualquer
    uma delas cria outra pasta e evita misturar progresso incompatível."""
    partes = [config["inicio"], config["fim"], config.get("versao_selecao", "selecao_v1")]

    if config.get("versao_selecao", "selecao_v1") != "selecao_v1":
        partes.append(config.get("semente_amostragem"))

    return hashlib.sha256(json.dumps(partes).encode()).hexdigest()[:12]


def pasta_janela(config):
    return Path(config.get("diretorio_saida", "dados")) / f"janela_{chave_janela(config)}"
