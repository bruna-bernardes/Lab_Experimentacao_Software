"""Aplica os testes da Sprint 1 aos dados observados."""
import pandas as pd
from .estatistica import testar, META, ALFA


def tabela_dados_reais(df):
    resultado = testar(df['falha'].to_numpy())
    diferenca = resultado['taxa'] - META
    return pd.DataFrame([
        {'Teste': 'Teste Z', 'Estatística': f"Z = {resultado['z']:.3f}",
         'p-valor': f"{resultado['p_z']:.4f}", 'Tamanho do efeito': f'{diferenca * 100:+.1f} p.p.',
         'Conclusão': 'Rejeita H₀' if resultado['p_z'] < ALFA else 'Não rejeita H₀'},
        {'Teste': 'Binomial exato', 'Estatística': f"k = {resultado['falhas']}/{resultado['n']}",
         'p-valor': f"{resultado['p_exato']:.4f}", 'Tamanho do efeito': f'{diferenca * 100:+.1f} p.p.',
         'Conclusão': 'Rejeita H₀' if resultado['p_exato'] < ALFA else 'Não rejeita H₀'},
    ])
