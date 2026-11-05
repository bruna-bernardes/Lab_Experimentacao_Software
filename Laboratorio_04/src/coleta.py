"""Coleta de execuções concluídas do GitHub Actions (API pública)."""
import argparse
import os
import time
import requests
import pandas as pd


def coletar(repo: str, quantidade: int = 100) -> pd.DataFrame:
    if quantidade < 1:
        raise ValueError('quantidade deve ser positiva')
    linhas = []
    pagina = 1
    headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    while len(linhas) < quantidade:
        url = f'https://api.github.com/repos/{repo}/actions/runs'
        resposta = requests.get(url, params={'per_page': 100, 'page': pagina, 'status': 'completed'}, headers=headers, timeout=30)
        resposta.raise_for_status()
        runs = resposta.json().get('workflow_runs', [])
        if not runs:
            break
        for run in runs:
            conclusao = run.get('conclusion')
            if conclusao not in ('success', 'failure'):
                continue
            linhas.append({'run_id': run['id'], 'repositorio': repo, 'conclusao': conclusao, 'falha': int(conclusao == 'failure'), 'created_at': run.get('created_at'), 'html_url': run.get('html_url')})
            if len(linhas) >= quantidade:
                break
        pagina += 1
        time.sleep(0.1)
    if not linhas:
        raise RuntimeError('Nenhuma execução válida encontrada. Escolha outro repositório.')
    return pd.DataFrame(linhas)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='pallets/flask')
    parser.add_argument('--n', type=int, default=100)
    args = parser.parse_args()
    df = coletar(args.repo, args.n)
    destino = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'execucoes_ci.csv')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    df.to_csv(destino, index=False)
    print(f'{len(df)} execuções válidas; falhas: {df.falha.sum()}; taxa: {df.falha.mean():.2%}')
