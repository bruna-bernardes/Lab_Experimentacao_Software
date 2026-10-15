# 1. Introdução

As métricas DORA (*DevOps Research and Assessment*) são utilizadas para avaliar o desempenho da entrega de software, considerando aspectos de velocidade e estabilidade. Entre as métricas clássicas estão a frequência de deploy, o tempo entre o commit e a entrega, a taxa de falhas e o tempo de recuperação após falhas.

Em projetos de código aberto, essas métricas podem ser investigadas a partir de informações disponibilizadas pelo GitHub, como releases, commits e execuções do GitHub Actions. Entretanto, esses dados representam aproximações das métricas DORA, pois uma release não corresponde necessariamente a uma implantação em produção, assim como uma falha de integração contínua não indica obrigatoriamente uma falha em produção.

Este trabalho tem como objetivo investigar o desempenho de entrega de repositórios populares do GitHub que utilizam CI/CD, por meio da coleta automatizada e análise de métricas DORA. Também busca compreender como características dos projetos e diferentes definições operacionais podem influenciar os resultados.

## 1.1 Questões de pesquisa e hipóteses

**RQ01 — Qual a frequência de deploys dos repositórios populares que usam CI/CD?**

Hipótese: espera-se que os repositórios apresentem frequências de entrega variadas, devido às diferenças entre os processos de desenvolvimento e publicação de cada projeto.

**RQ02 — Qual o tempo entre um commit e seu respectivo deploy?**

Hipótese: espera-se que o lead time calculado por release seja maior do que o calculado por commit, pois a primeira variante considera o commit mais antigo incluído em cada release.

**RQ03 — Qual a taxa de falha das mudanças entregues por esses repositórios?**

Hipótese: espera-se que o proxy baseado em falhas de CI apresente resultados diferentes do proxy baseado em releases corretivas, pois representam tipos distintos de falha.

**RQ04 — Qual o tempo de recuperação após uma execução de CI/CD com falha?**

Hipótese: espera-se que os tempos de recuperação variem entre os repositórios, refletindo diferenças na capacidade de identificar e corrigir falhas.

**RQ05 — Repositórios com maior frequência de deploy apresentam maior ou menor taxa de falha?**

Hipótese: espera-se que uma maior frequência de entregas não esteja necessariamente associada a uma maior taxa de falhas.

**RQ06 — Quais características dos repositórios estão associadas a um melhor desempenho DORA?**

Hipótese: espera-se que características como linguagem principal, popularidade e quantidade de contribuidores apresentem associações com as métricas de desempenho.

**RQ07 — O quanto a classificação DORA de um repositório depende da definição operacional escolhida?**

Hipótese: espera-se que a utilização de diferentes definições operacionais provoque alterações na classificação de parte dos repositórios, demonstrando sensibilidade às aproximações utilizadas.

Essas hipóteses serão investigadas nas próximas etapas do laboratório, utilizando os dados coletados e métodos de análise estatística previstos no estudo.
# 2. Metodologia

## 2.2 Critérios de seleção e funil

Um repositório candidato foi incluído na amostra final quando, dentro da janela de observação, possuía pelo menos 5 releases publicadas (`draft = false`, `prerelease = false`) e pelo menos 50 *workflow runs* válidas no *default branch*, disparadas por `push` e com `conclusion` igual a `success`, `failure`, `timed_out` ou `startup_failure`. Os filtros foram aplicados em ordem crescente de custo de API: uso de GitHub Actions (`total_count > 0` em `/actions/workflows`), número de releases e número de runs. Os metadados mais custosos, como a contagem de contribuidores, foram coletados apenas para os repositórios elegíveis. Repositórios com erro persistente após três tentativas foram registrados separadamente.

A Tabela X apresenta o funil de seleção (`resultados/funil_selecao.csv`):

| Etapa | Repositórios |
|---|---|
| População da busca | `<pendente>` |
| Candidatos examinados | `<pendente>` |
| Sem GitHub Actions | `<pendente>` |
| Com GitHub Actions | `<pendente>` |
| Menos de 5 releases na janela | `<pendente>` |
| Menos de 50 runs válidas na janela | `<pendente>` |
| Erros persistentes | `<pendente>` |
| **Amostra final** | `<pendente>` |

## 2.3 Janela de observação e coleta

A janela de observação compreende 12 meses, de `<pendente: início>` a `<pendente: fim>`, conforme definido pelo professor. Apenas releases publicadas e runs criadas nesse intervalo entram nos cálculos. Para identificar a release anterior no cálculo do lead time, foi usado o histórico completo de releases do repositório.

A coleta foi executada entre `<pendente: datas>` (`resultados/log_coleta.md`). Cada resposta da API foi armazenada em cache local, o que permitiu retomar a coleta após interrupções sem repetir chamadas. O pipeline respeita os cabeçalhos `X-RateLimit-Remaining` e `X-RateLimit-Reset` e repete erros temporários (5xx) com *backoff* exponencial. As runs foram consultadas mês a mês, e os períodos com 1.000 resultados ou mais foram subdivididos automaticamente. As comparações entre releases (`/compare/{anterior}...{atual}`) foram paginadas para superar o limite de 250 commits. Os dados intermediários (releases, commits e runs) e o dataset final foram exportados para arquivos CSV versionados, cujas colunas estão descritas no dicionário de dados (`resultados/dicionario_dados.md`).
