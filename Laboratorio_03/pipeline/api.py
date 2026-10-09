
import os
import json
import time
import hashlib
import requests
from pathlib import Path


class GitHubAPI:
    def __init__(self, token=None, cache_dir=".cache/github"):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("Configure a variável de ambiente GITHUB_TOKEN.")

        self.base_url = "https://api.github.com"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

    def get(self, endpoint, params=None):
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        chave = hashlib.sha256(json.dumps([url, params], sort_keys=True).encode()).hexdigest()
        arquivo = self.cache_dir / f"{chave}.json"

        if arquivo.exists():
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)

        for tentativa in range(6):
            try:
                resposta = self.session.get(url, params=params, timeout=60)

                if resposta.status_code in (403, 429):
                    restante = resposta.headers.get("X-RateLimit-Remaining")
                    reset = resposta.headers.get("X-RateLimit-Reset")

                    if restante == "0" and reset:
                        espera = max(1, int(reset) - int(time.time()) + 2)
                        print(f"Rate limit atingido. Aguardando {espera}s...")
                        time.sleep(espera)
                        continue

                    if resposta.status_code == 429 or resposta.headers.get("Retry-After"):
                        espera = int(resposta.headers.get("Retry-After", 2 ** tentativa))
                        time.sleep(espera)
                        continue

                if resposta.status_code in (500, 502, 503, 504):
                    time.sleep(2 ** tentativa)
                    continue

                resposta.raise_for_status()

                resultado = {"data": resposta.json(), "headers": dict(resposta.headers)}

                with open(arquivo, "w", encoding="utf-8") as f:
                    json.dump(resultado, f, ensure_ascii=False)

                return resultado

            except (requests.Timeout, requests.ConnectionError):
                if tentativa == 5:
                    raise
                time.sleep(2 ** tentativa)

        raise RuntimeError(f"Falha ao consultar a API: {url}")

    def paginas(self, endpoint, params=None, limite=None):
        resultados = []
        params = dict(params or {})
        params.setdefault("per_page", 100)
        url = endpoint

        while url:
            resposta = self.get(url, params)
            dados = resposta["data"]

            if isinstance(dados, dict):
                dados = dados.get("items", [])

            resultados.extend(dados)

            if limite is not None and len(resultados) >= limite:
                return resultados[:limite]

            links = requests.utils.parse_header_links(
                resposta["headers"].get("Link", "").replace(">,<", ">, <")
            )
            proximo = next((link["url"] for link in links if link.get("rel") == "next"), None)

            url = proximo
            params = None

        return resultados
