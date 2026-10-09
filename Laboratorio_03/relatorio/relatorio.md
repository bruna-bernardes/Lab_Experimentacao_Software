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