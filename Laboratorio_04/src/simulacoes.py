"""Sprint 2: Monte Carlo reprodutível para erro tipo I e poder."""
import numpy as np
import pandas as pd
from scipy.stats import binomtest, norm
from .estatistica import META, ALFA

REPETICOES = 10_000
EFEITOS = np.array([0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.10])


def executar_simulacoes(n_real, repeticoes=REPETICOES, seed=42):
    """Compara n real e n pequeno (20), preservando H0 e os testes bicaudais.

    Tamanho de efeito é a diferença absoluta p - 0.05 (pontos proporcionais).
    A situação de n=20 viola o critério usual np0 >= 5 da aproximação normal.
    """
    if n_real <= 0 or repeticoes <= 0:
        raise ValueError('n_real e repeticoes precisam ser positivos')
    rng = np.random.default_rng(seed)
    linhas = []
    for situacao, n in [('Amostra real', int(n_real)), ('Amostra pequena', 20)]:
        ks = np.arange(n + 1)
        p_exatos = np.array([binomtest(int(k), n, META).pvalue for k in ks])
        z = (ks / n - META) / np.sqrt(META * (1 - META) / n)
        p_z = 2 * norm.sf(np.abs(z))
        for efeito in EFEITOS:
            p = META + float(efeito)
            contagens = rng.binomial(n, p, size=repeticoes)
            for nome, valores in [('Teste Z', p_z), ('Binomial exato', p_exatos)]:
                taxa = float(np.mean(valores[contagens] < ALFA))
                linhas.append({'situacao': situacao, 'n': n, 'teste': nome,
                               'efeito': float(efeito), 'p_verdadeiro': p,
                               'taxa_rejeicao': taxa, 'repeticoes': repeticoes})
    return pd.DataFrame(linhas)
