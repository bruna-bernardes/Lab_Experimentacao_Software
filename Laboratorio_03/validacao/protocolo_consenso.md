# Protocolo de resolução de divergências — Lab03S02

Definido **antes** da reunião de consenso e commitado antes do arquivo de decisões.

1. **Rotulagem independente.** Cada avaliador rotula sozinho os 60 repositórios e as releases sorteadas (`guia_rotulagem.md`). Os três arquivos são commitados antes de qualquer discussão.
2. **Concordância.** `python -m validacao.concordancia` calcula o kappa de Fleiss por dimensão e gera `divergencias.csv`. Os kappas são reportados no artigo **antes** do consenso, como medida da ambiguidade do critério.
3. **Regra automática.**
   - 3-0 (unanimidade): o rótulo é aceito (`origem = unanime`).
   - 2-1 (maioria simples): vale o rótulo da maioria (`origem = maioria`).
4. **Empates 1-1-1** (só ocorrem em `tipo_projeto` e `entregas_reais`): decididos em reunião com os três avaliadores. Cada um apresenta o argumento; a decisão é registrada em `decisoes_reuniao.csv`, com justificativa obrigatória, data e presentes (`origem = reuniao`).
5. **Revisão de maiorias.** Casos 2-1 **não** são rediscutidos por padrão. Se, durante a reunião, o grupo identificar um erro claro de leitura (por exemplo, link errado), a correção também vai para `decisoes_reuniao.csv` com justificativa.
6. **Consenso final.** `python -m validacao.consenso` gera `consenso_repositorios.csv` e `consenso_releases.csv` e interrompe a execução se algum empate não tiver decisão registrada.
7. **Uso.** O consenso de `corretiva` é a referência para precisão, recall e F1 da heurística. O consenso de `tipo_projeto` alimenta a RQ 06. A contagem por `origem` é reportada na Metodologia.
