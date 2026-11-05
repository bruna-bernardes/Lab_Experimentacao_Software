"""Simulação reprodutível e comparação de dois testes bicaudais."""
import numpy as np
from scipy.stats import binomtest, norm

ALFA = 0.05
META = 0.05
SEMENTE = 42


def simular(n: int, proporcao: float, seed: int = SEMENTE) -> np.ndarray:
    return np.random.default_rng(seed).binomial(1, proporcao, size=n)


def testar(amostra: np.ndarray, p0: float = META) -> dict:
    n = len(amostra)
    if n == 0 or not 0 < p0 < 1:
        raise ValueError('Amostra não vazia e 0 < p0 < 1 são necessários')
    k = int(np.sum(amostra))
    phat = k / n
    z = (phat - p0) / np.sqrt(p0 * (1 - p0) / n)
    p_z = float(2 * norm.sf(abs(z)))
    p_exato = float(binomtest(k, n, p=p0, alternative='two-sided').pvalue)
    return {'n': n, 'falhas': k, 'taxa': phat, 'z': float(z), 'p_z': p_z,
            'p_exato': p_exato, 'rejeita_z': p_z < ALFA,
            'rejeita_exato': p_exato < ALFA}


if __name__ == '__main__':
    print(testar(simular(100, META)))
