# Dashboard — Gráficos do Experimento (Sprint 3)

Gerados com `python scripts/gerar_dashboard.py` (Pandas + Matplotlib + Seaborn)
a partir de `dados/resultados_trials.csv` e `dados/metricas_estaticas.csv`.

| Arquivo | Questão | Descrição |
|---|---|---|
| `rq1_tempo_por_tratamento.png` | RQ1 | Boxplot do time-to-green por tratamento (escala logarítmica por causa do outlier da Bruna em kata_03/kata_02 SEM_IA), com os 12 trials sobrepostos |
| `rq2_taxa_sucesso_por_kata.png` | RQ2 | Barras agrupadas da taxa de sucesso média por kata × tratamento (100% em todas as células) |
| `rq3_metricas_por_tratamento.png` | RQ3 | Boxplots de CC média, Maintainability Index e LOC por tratamento |
| `rq3_cc_por_loc.png` | RQ3 | Scatter CC × LOC com identificação de cada trial (controle de verbosidade) |
| `correlacao_metricas.png` | RQ3 | Heatmap de correlação de Spearman entre as métricas (coluna de duplicação vazia porque todos os valores são 0) |

Como executar:

```bash
python scripts/gerar_dashboard.py
```

Dependências: pandas, matplotlib, seaborn (adicionar ao requirements.txt se necessário).
