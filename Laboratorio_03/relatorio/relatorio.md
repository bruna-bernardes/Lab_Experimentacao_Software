# Mineração de métricas DORA em repositórios públicos

## 1. Introdução

As métricas DORA avaliam velocidade e estabilidade da entrega de software.
Este estudo usa releases públicas como proxy de deploy, execuções do GitHub
Actions como proxy de integração e commits como origem do lead time. Como o
GitHub não registra diretamente deploys em produção nem incidentes de
produção, os resultados devem ser interpretados como aproximações.

### 1.1 Questões de pesquisa e hipóteses

**RQ01.** Qual a frequência de deploy dos repositórios populares que usam
CI/CD? Esperamos grande dispersão entre projetos.

**RQ02.** Qual o tempo entre commit e deploy? Esperamos que a variante por
release seja maior que a variante por commit, pois usa o commit mais antigo de
cada release.

**RQ03.** Qual a taxa de falha? Esperamos diferenças entre o proxy de falha de
CI e o proxy de releases corretivas.

**RQ04.** Qual o tempo de recuperação? Esperamos heterogeneidade entre os
repositórios.

**RQ05.** Frequência maior implica maior CFR? Esperamos que velocidade e
estabilidade não apresentem uma relação monotônica forte.

**RQ06.** Quais características estão associadas ao desempenho? Esperamos
associações com linguagem, popularidade e idade.

**RQ07.** A classificação depende da definição operacional? Esperamos que parte
dos repositórios mude de categoria entre variantes.

## 2. Metodologia

### 2.1 Amostra e coleta

Foram considerados repositórios públicos não arquivados, não fork, com mais de
1.000 estrelas, GitHub Actions, pelo menos cinco releases publicadas e pelo
menos 50 workflow runs válidas na janela de 01/10/2025 a 30/09/2026. A
amostragem usou semente 42 e buscou 320 repositórios para manter margem acima
do mínimo de 300.

| Etapa | Repositórios |
|---|---:|
| População da busca | 60.162 |
| Candidatos examinados | 2.255 |
| Sem GitHub Actions | 934 |
| Com GitHub Actions | 1.320 |
| Menos de 5 releases | 886 |
| Menos de 50 runs válidas | 114 |
| Erros persistentes | 1 |
| **Amostra final** | **320** |

O pipeline, o cache, a exportação e as regras de cálculo estão documentados
em `README.md`. O dataset final e seu dicionário estão em
`resultados/dataset_final.csv` e `resultados/dicionario_dados.md`.

### 2.2 Definições operacionais

Deployment frequency é o número de releases por semana. O lead time foi
calculado por release e por commit usando `commit.author.date` e
`published_at`. O CFR de CI é a proporção de runs com conclusão
`failure`, `timed_out` ou `startup_failure` entre falhas e sucessos. O CFR de
entrega marca uma release como falha quando é seguida por uma release
corretiva em até sete dias. O tempo de recuperação é medido do início da
primeira falha até o `updated_at` do sucesso seguinte no mesmo workflow.

Todas as estatísticas usam mediana e intervalo interquartil. As categorias DORA
usam os cortes fixos definidos no enunciado.

### 2.3 Validação da amostra-ouro

A amostra-ouro contém 60 repositórios e 300 releases. A concordância de Fleiss
foi moderada para tipo de projeto (κ = 0,5177), pobre para entregas reais
(κ = -0,0403) e razoável para releases corretivas (κ = 0,3687). A
concordância unânime foi, respectivamente, 80,0%, 40,0% e 52,7%.

O consenso foi composto por 48 rótulos unânimes e 12 por maioria para tipo de
projeto; 24 unânimes, 32 por maioria e 4 decisões de reunião para entregas
reais; e 158 unânimes e 142 por maioria para releases corretivas.

| Versão | Precisão | Recall | F1 |
|---|---:|---:|---:|
| v1 | 0,833 | 0,611 | 0,705 |
| v2 | 0,809 | 0,198 | 0,318 |
| v3 | 0,828 | 0,756 | 0,790 |

A versão v3 foi escolhida para análises futuras por apresentar o maior F1. Os
resultados detalhados estão em `validacao/heuristica_versoes.csv`.

## 3. Resultados

As tabelas e figuras desta seção foram geradas por
`python analise_sprint3.py` e estão em `resultados/sprint3/`.

### 3.1 RQ01 — Deployment frequency

A mediana foi **0,345 releases/semana**, com Q1 = 0,173, Q3 = 0,901 e
IQR = 0,729. A distribuição é assimétrica e indica que a maior parte da
amostra está abaixo de uma release por semana. O histograma está em
`resultados/sprint3/rq01_frequency.png`.

### 3.2 RQ02 — Lead time

| Variante | n | Mediana (h) | Q1 (h) | Q3 (h) | IQR (h) |
|---|---:|---:|---:|---:|---:|
| Por release | 320 | 245,25 | 41,06 | 760,99 | 719,93 |
| Por commit | 320 | 193,41 | 45,46 | 673,83 | 628,37 |

A mediana por release foi maior, conforme a hipótese. A diferença é
compatível com o efeito de um commit antigo elevar o valor representativo da
release, enquanto a variante por commit distribui a contribuição entre todos
os commits.

### 3.3 RQ03 — Change failure rate

| Variante | n | Mediana | Q1 | Q3 | IQR |
|---|---:|---:|---:|---:|---:|
| CFR de CI | 320 | 0,048 | 0,021 | 0,122 | 0,101 |
| CFR de entrega | 320 | 0,200 | 0,020 | 0,444 | 0,424 |

O CFR de entrega é maior e mais disperso. Isso reforça que falha de pipeline e
release corretiva não são o mesmo construto. O resultado apoia a hipótese de
que as duas aproximações produzem conclusões diferentes.

### 3.4 RQ04 — Tempo de recuperação

Foram observados 292 repositórios com valor válido. A mediana foi **3,06
horas**, Q1 = 0,87, Q3 = 16,77 e IQR = 15,89. Vinte e oito repositórios não
possuíam episódio recuperado observável na janela, portanto foram tratados
como ausentes na mediana e devem ser considerados na discussão sobre censura.

### 3.5 RQ05 — Frequência versus falha

| CFR | n | Spearman rho | p-valor |
|---|---:|---:|---:|
| CFR de CI | 320 | 0,072 | 0,197 |
| CFR de entrega | 320 | 0,461 | < 0,001 |

Não houve evidência de associação monotônica significativa entre frequência e
CFR de CI. Para CFR de entrega houve associação positiva moderada. O resultado
não permite inferir causalidade: releases mais frequentes podem refletir
projetos com ciclos e políticas diferentes. Os gráficos estão em
`resultados/sprint3/rq05_cfr_ci.png` e `rq05_cfr_entrega.png`.

### 3.6 RQ06 — Características associadas

Foram avaliados linguagem, quartis de estrelas e quartis de idade. Aplicou-se
Kruskal-Wallis e correção de Holm. Os tamanhos de efeito epsilon quadrado e os
p-valores completos estão em `resultados/sprint3/rq06_testes.csv`. Também foi
incluído o fator tipo de projeto, comparando biblioteca/framework,
aplicação/serviço e ferramenta CLI.

Após Holm, linguagem foi associada a frequência e às duas variantes de lead
time, mas não aos CFR ou à recuperação. Estrelas não apresentou resultado
significativo após correção. Idade foi associada a frequência, às duas
variantes de lead time e ao CFR de entrega. O fator tipo de projeto também foi
incluído após a consolidação da amostra-ouro. Os efeitos observados são
associações entre grupos, não evidência de causalidade.

### 3.7 RQ07 — Sensibilidade da classificação

Foram usadas três configurações reproduzíveis com os campos disponíveis:

- **C1:** lead time por release e CFR de CI;
- **C2:** lead time por commit e CFR de entrega;
- **C3:** lead time por release e CFR de entrega.

| Comparação | Mudança de categoria | Percentual | Kappa ponderado |
|---|---:|---:|---:|
| C1 × C2 | 118/320 | 36,88% | 0,428 |
| C1 × C3 | 84/320 | 26,25% | 0,586 |
| C2 × C3 | 55/320 | 17,19% | 0,712 |

As classificações não são completamente robustas à definição escolhida. A
maior diferença ocorre quando se trocam simultaneamente a variante de lead
time e o proxy de falha. As três configurações analisadas estão disponíveis no
arquivo de resultados para reprodução.

## 4. Discussão

Os resultados confirmam a heterogeneidade esperada. O lead time por release é
maior que o lead time por commit, e os dois CFRs têm níveis e dispersões
distintos. A ausência de correlação significativa com CFR de CI é compatível
com a expectativa de que velocidade não implique automaticamente instabilidade.
Já a associação com CFR de entrega mostra que a escolha do proxy altera a
conclusão.

Linguagem e idade apresentaram diferenças entre grupos, enquanto popularidade
não foi significativa após correção múltipla. Isso indica que fatores de
contexto podem ser mais informativos que estrelas isoladamente. A análise de
sensibilidade mostrou que entre 17,81% e 33,75% dos repositórios mudam de
categoria, portanto a classificação geral deve sempre informar sua definição.

## 5. Ameaças à validade

**Construto.** Release não é necessariamente deploy em produção e uma falha
de CI não é necessariamente uma falha de produção. A heurística de releases
corretivas também depende de mensagens e versionamento.

**Interna.** Idade, linguagem, política de release, tamanho do projeto e
workflows podem atuar como confundidores. A análise observacional não controla
esses fatores nem estabelece causalidade.

**Externa.** A amostra contém projetos públicos populares com mais de 1.000
estrelas e não representa necessariamente projetos corporativos, privados ou
menos populares.

**Conclusão.** Há múltiplas comparações em RQ06, embora Holm reduza falsos
positivos. Valores ausentes de recuperação e a ausência dos rótulos preenchidos
limitam a interpretação. O uso de medianas e IQR reduz o efeito de outliers,
mas não elimina vieses de coleta.

## 6. Replicação cruzada

Para a execução futura, a amostra fixa de 30 repositórios está em
`resultados/replicacao/amostra_30.csv` e o utilitário de comparação está em
`replicacao.py`. O responsável pela replicação deverá registrar nesta seção o
grupo replicador, o repositório avaliado, o comando, as diferenças relativas
por métrica, a classificação DORA e os links das Issues abertas e respondidas.
O pipeline autoral deve ser executado com:

```powershell
python -m pipeline --config config.json
```

## 7. Conclusão

O estudo mostra que métricas DORA inferidas de GitHub variam
substancialmente entre repositórios e dependem da definição operacional. A
frequência mediana foi baixa, os lead times foram assimétricos, e CFR de CI e
CFR de entrega produziram sinais diferentes. A análise de sensibilidade
demonstrou que a classificação não deve ser interpretada sem explicitar os
proxies empregados.

## Referências

- Forsgren, N.; Humble, J.; Kim, G. *Accelerate*. IT Revolution, 2018.
- DORA. *Software delivery metrics: the four keys*.
- Wohlin, C. et al. *Experimentation in Software Engineering*. Springer.
- Landis, J. R.; Koch, G. G. The measurement of observer agreement for
  categorical data. *Biometrics*, 1977.
