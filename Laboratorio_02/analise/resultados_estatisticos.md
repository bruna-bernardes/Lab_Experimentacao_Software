# Resultados Estatísticos — Lab02

Desenho: crossover within-subject contrabalanceado (3 participantes × 4 katas = 12 trials, 6 por tratamento).

Como cada participante resolveu cada kata apenas uma vez, o pareamento do Wilcoxon foi feito agregando por participante (média dos 2 katas de cada tratamento) para RQ1 e RQ2, e agregando por kata (média dos 3 participantes) para RQ3.

H0: a distribuição das amostras pareadas é a mesma entre os tratamentos. Tamanho de efeito: Cliff's delta — positivo indica valores maiores em SEM_IA; negativo, valores maiores em COM_IA.

## RQ1 — Tempo (time-to-green)

### Tempo médio por participante (média dos 2 katas de cada tratamento)

**Unidade:** segundos

| Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|
| COM_IA | 19.30 | 19.30 | 147.16 | 127.86 |
| SEM_IA | 74.52 | 63.50 | 622.40 | 558.89 |

- Wilcoxon pareado (n = 3): p-valor = **0.2500** — não rejeita H0 (sem diferença significativa) (alfa = 0.05)
- Cliff's delta: **-0.556** (grande)
- Comparação por pares: valor maior em SEM_IA em 3 par(es), maior em COM_IA em 0 par(es), empate em 0 par(es)

Considerando todos os 6 trials por tratamento, a mediana do time-to-green foi de 0.34 min no COM_IA contra 1.50 min no SEM_IA (redução de 77.3% com o uso da IA).

## RQ2 — Defeitos (taxa de sucesso dos testes)

### Taxa de sucesso dos testes (média por participante)

**Unidade:** percentual

| Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|
| COM_IA | 100.00 | 100.00 | 100.00 | 0.00 |
| SEM_IA | 100.00 | 100.00 | 100.00 | 0.00 |

- Wilcoxon pareado (n = 3): p-valor = **1.0000** — não rejeita H0 (sem diferença significativa) (alfa = 0.05)
- Cliff's delta: **+0.000** (negligenciável)
- Comparação por pares: valor maior em SEM_IA em 0 par(es), maior em COM_IA em 0 par(es), empate em 3 par(es)

Contagem absoluta de testes falhando ao final: COM_IA = 0, SEM_IA = 0. Todos os 12 trials concluíram com 100% de sucesso (variância zero), impedindo qualquer conclusão estatística sobre defeitos neste experimento.

## RQ3 — Estrutura do código (métricas estáticas)

### Complexidade ciclomática média (Radon cc)

**Unidade:** CC

| Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|
| COM_IA | 10.00 | 9.75 | 13.25 | 3.50 |
| SEM_IA | 10.75 | 9.38 | 12.25 | 2.88 |

- Wilcoxon pareado (n = 4): p-valor = **0.7500** — não rejeita H0 (sem diferença significativa) (alfa = 0.05)
- Cliff's delta: **+0.062** (negligenciável)
- Comparação por pares: valor maior em SEM_IA em 1 par(es), maior em COM_IA em 2 par(es), empate em 1 par(es)

### Duplicação de código (jscpd)

**Unidade:** percentual

| Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|
| COM_IA | 0.00 | 0.00 | 0.00 | 0.00 |
| SEM_IA | 0.00 | 0.00 | 0.00 | 0.00 |

- Wilcoxon pareado (n = 4): p-valor = **1.0000** — não rejeita H0 (sem diferença significativa) (alfa = 0.05)
- Cliff's delta: **+0.000** (negligenciável)
- Comparação por pares: valor maior em SEM_IA em 0 par(es), maior em COM_IA em 0 par(es), empate em 4 par(es)

### Maintainability Index (Radon mi)

**Unidade:** índice

| Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|
| COM_IA | 54.38 | 51.96 | 54.67 | 2.72 |
| SEM_IA | 52.48 | 51.60 | 53.46 | 1.86 |

- Wilcoxon pareado (n = 4): p-valor = **0.8750** — não rejeita H0 (sem diferença significativa) (alfa = 0.05)
- Cliff's delta: **+0.500** (grande)
- Comparação por pares: valor maior em SEM_IA em 1 par(es), maior em COM_IA em 3 par(es), empate em 0 par(es)

### LOC (métrica de controle)

**Unidade:** linhas

| Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|
| COM_IA | 40.75 | 34.12 | 47.25 | 13.12 |
| SEM_IA | 39.75 | 36.75 | 40.75 | 4.00 |

- Wilcoxon pareado (n = 4): p-valor = **0.8750** — não rejeita H0 (sem diferença significativa) (alfa = 0.05)
- Cliff's delta: **+0.188** (pequeno)
- Comparação por pares: valor maior em SEM_IA em 1 par(es), maior em COM_IA em 3 par(es), empate em 0 par(es)

## Notas sobre o poder estatístico

Com n = 3 pares (por participante, RQ1/RQ2) ou n = 4 pares (por kata, RQ3), o menor p-valor bilateral possível no Wilcoxon é 0,25 (n = 3) e 0,125 (n = 4) — nunca abaixo de alfa = 0,05. Os resultados são, portanto, descritivos e exploratórios; o tamanho de efeito (Cliff's delta) é a informação mais relevante neste tamanho de amostra.
A variância zero em RQ2 (100% de sucesso em todos os trials) impede qualquer conclusão sobre diferença de defeitos entre os tratamentos neste experimento.
