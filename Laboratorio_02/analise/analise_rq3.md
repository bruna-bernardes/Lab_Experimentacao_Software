# Análise Detalhada da RQ3 — Estrutura do Código

Análise complementar da RQ3 com foco em complexidade ciclomática, duplicação e LOC por tratamento, usando LOC como métrica de controle.

## Métricas por trial

| Participante | Kata | Tratamento | LOC | CC média | MI | Duplicação % |
|---|---|---|---|---|---|---|
| Bruna | kata_01 | COM_IA | 30 | 10.0 | 54.64 | 0.0 |
| Bruna | kata_02 | SEM_IA | 30 | 9.0 | 54.09 | 0.0 |
| Bruna | kata_03 | SEM_IA | 38 | 13.0 | 51.68 | 0.0 |
| Bruna | kata_04 | COM_IA | 43 | 9.0 | 54.95 | 0.0 |
| Walter | kata_04 | COM_IA | 49 | 11.0 | 53.29 | 0.0 |
| Walter | kata_02 | COM_IA | 36 | 8.0 | 54.28 | 0.0 |
| Walter | kata_03 | SEM_IA | 43 | 13.0 | 50.85 | 0.0 |
| Walter | kata_01 | SEM_IA | 37 | 10.0 | 52.05 | 0.0 |
| Ana | kata_01 | SEM_IA | 46 | 9.0 | 54.46 | 0.0 |
| Ana | kata_02 | COM_IA | 35 | 10.0 | 55.28 | 0.0 |
| Ana | kata_03 | COM_IA | 51 | 23.0 | 45.47 | 0.0 |
| Ana | kata_04 | SEM_IA | 39 | 12.0 | 51.71 | 0.0 |

## Resumo por tratamento (mediana e IQR)

| Métrica | Tratamento | Mediana | Q1 | Q3 | IQR |
|---|---|---|---|---|---|
| LOC | COM_IA | 39.50 | 35.25 | 47.50 | 12.25 |
| LOC | SEM_IA | 38.50 | 37.25 | 42.00 | 4.75 |
| CC média | COM_IA | 10.00 | 9.25 | 10.75 | 1.50 |
| CC média | SEM_IA | 11.00 | 9.25 | 12.75 | 3.50 |
| Maintainability Index | COM_IA | 54.46 | 53.54 | 54.87 | 1.34 |
| Maintainability Index | SEM_IA | 51.88 | 51.69 | 53.58 | 1.89 |

## Complexidade normalizada por LOC (CC/LOC)

- COM_IA: mediana de CC/LOC = 0.2857
- SEM_IA: mediana de CC/LOC = 0.3023

## Discussão

1. **Duplicação:** nenhum trial apresentou linhas duplicadas (0% em todos), então este experimento não conseguiu diferenciar os tratamentos por essa métrica. Isso é esperado em soluções de katas pequenos, com uma única função cada.
2. **Complexidade ciclomática:** as medianas ficaram próximas entre os tratamentos (10.00 no COM_IA contra 11.00 no SEM_IA), mas a dispersão no SEM_IA é maior (IQR 3.50 contra 1.50). O código manual variou mais de estilo entre trials — no kata_03 da Ana, o assistente produziu CC 23.0, o outlier mais alto de todo o experimento.
3. **LOC como controle:** a IA não gerou código sistematicamente mais verboso neste experimento — a mediana de LOC é praticamente igual entre os tratamentos (39.50 contra 38.50), embora o COM_IA tenha IQR maior (12.25 contra 4.75). Sem essa checagem, diferenças de complexidade poderiam ser interpretadas incorretamente como mais verbosidade da IA.
4. **Maintainability Index:** o COM_IA apresentou mediana maior (54.46 contra 51.88) e IQR menor (1.34 contra 1.89), sugerindo código estruturalmente mais manutenível e mais uniforme entre os trials.
5. **Limitação:** com 6 trials por tratamento e katas de domínio simples, estas observações são exploratórias e não generalizáveis; servem de base para a discussão do relatório final.
