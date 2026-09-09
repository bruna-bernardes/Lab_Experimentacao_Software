# LAB02 — Assistentes de IA vs. Codificação Manual: um Experimento Controlado

## Sprint 01 — Desenho e Preparação do Experimento

**Disciplina:** Laboratório de Experimentação de Software  
**Curso:** Engenharia de Software  
**Período:** 6º  
**Professor:** Danilo Maia  

---

# 1. Objetivo do experimento

Este experimento tem como objetivo avaliar quantitativamente o impacto do uso de um assistente de Inteligência Artificial Generativa na resolução de tarefas de programação.

Será realizada uma comparação entre dois tratamentos:

- resolução da tarefa com auxílio de um assistente de IA;
- resolução da tarefa por meio de codificação manual, sem utilização de assistentes de IA.

Serão avaliados três aspectos principais:

1. tempo necessário para resolver a tarefa;
2. qualidade funcional, medida pela quantidade e proporção de testes automatizados aprovados;
3. qualidade estrutural do código, considerando complexidade ciclomática, duplicação e quantidade de linhas de código.

O experimento será realizado utilizando a linguagem **Python** e adotará um desenho **crossover within-subject contrabalanceado**, permitindo que cada participante realize tarefas nos dois tratamentos.

---

# 2. Questões de Pesquisa

## RQ1 — Tempo

**O uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação?**

## RQ2 — Defeitos

**O uso de assistente de IA reduz a quantidade de defeitos (testes que falham) no código produzido?**

## RQ3 — Estrutura

**O uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido?**

---

# 3. Hipóteses

## 3.1 RQ1 — Tempo de resolução

### Hipótese nula (H0₁)

O uso de um assistente de IA não reduz o tempo necessário para resolver as tarefas de programação em comparação com a codificação manual.

### Hipótese alternativa (H1₁)

O uso de um assistente de IA reduz o tempo necessário para resolver as tarefas de programação em comparação com a codificação manual.

Formalmente:

- **H0₁:** Mediana(Tempo_IA) ≥ Mediana(Tempo_Manual)
- **H1₁:** Mediana(Tempo_IA) < Mediana(Tempo_Manual)

---

## 3.2 RQ2 — Defeitos

### Hipótese nula (H0₂)

O uso de um assistente de IA não aumenta a taxa de testes de aceitação aprovados em comparação com a codificação manual.

### Hipótese alternativa (H1₂)

O uso de um assistente de IA aumenta a taxa de testes de aceitação aprovados em comparação com a codificação manual.

Formalmente:

- **H0₂:** Mediana(Sucesso_IA) ≤ Mediana(Sucesso_Manual)
- **H1₂:** Mediana(Sucesso_IA) > Mediana(Sucesso_Manual)

---

## 3.3 RQ3 — Qualidade estrutural

### Hipótese nula (H0₃)

O uso de um assistente de IA não altera significativamente as métricas de qualidade estrutural do código produzido.

### Hipótese alternativa (H1₃)

O uso de um assistente de IA altera significativamente as métricas de qualidade estrutural do código produzido.

Serão consideradas as seguintes métricas:

- complexidade ciclomática;
- percentual de código duplicado;
- linhas de código (LOC).

---

# 4. Variáveis do experimento

## 4.1 Variável independente

A variável independente é o **uso de assistente de IA generativa**.

A variável possui dois níveis:

| Tratamento | Descrição |
|---|---|
| IA | Participante pode utilizar o assistente de IA definido pelo grupo |
| Manual | Participante resolve a tarefa sem utilizar assistentes de IA |

O mesmo assistente de IA será utilizado em todos os trials pertencentes ao tratamento IA.

### Assistente selecionado

Será utilizado o **ChatGPT** como assistente de IA.

Durante a preparação e execução serão registrados:

- ferramenta utilizada;
- modelo utilizado, quando disponível;
- data da execução;
- linguagem utilizada;
- versão do Python;
- IDE utilizada.

---

# 5. Variáveis dependentes

## 5.1 Tempo de resolução

A métrica primária da RQ1 será o **time-to-green**.

O time-to-green corresponde ao tempo decorrido entre o início do trial e o momento em que todos os testes de aceitação são aprovados.

Cada trial terá um limite máximo de:

**35 minutos (2.100 segundos).**

Caso o participante não consiga concluir a tarefa dentro desse período, o trial será encerrado e registrado como **2.100 segundos**, não sendo descartado.

---

## 5.2 Taxa de sucesso dos testes

Para responder à RQ2 será registrada a taxa de testes de aceitação aprovados ao final de cada trial.

A métrica será calculada da seguinte maneira:

**Taxa de sucesso = (testes aprovados / total de testes) × 100**

Também será registrada a quantidade absoluta de testes que permaneceram falhando.

Essa abordagem permite comparar tarefas que possuam diferentes quantidades de testes.

---

## 5.3 Complexidade ciclomática

A complexidade ciclomática será utilizada para avaliar a complexidade estrutural do código.

Será utilizada a ferramenta **Radon**, por meio do comando de análise de complexidade ciclomática.

Será registrada principalmente a complexidade ciclomática média dos métodos/funções produzidos.

---

## 5.4 Duplicação de código

A duplicação de código será analisada utilizando a ferramenta **jscpd (JavaScript Copy/Paste Detector)**, que permite identificar trechos de código duplicados em diferentes linguagens, incluindo Python.

Será registrada a porcentagem de código duplicado encontrada no código final de cada trial.

---

## 5.5 Linhas de código (LOC)

Será registrada também a quantidade de linhas de código.

A LOC será utilizada como métrica de controle, permitindo contextualizar os resultados de complexidade e duplicação.

Isso é importante porque um código produzido por IA pode apresentar maior quantidade de linhas sem necessariamente possuir maior complexidade funcional.

---

## 5.6 Métrica exploratória — número de prompts

Nos trials realizados com IA será registrado, opcionalmente, o número de interações realizadas com o assistente.

Essa métrica terá caráter exploratório e poderá ser utilizada posteriormente na discussão dos resultados.

---

# 6. Tratamentos

## T1 — Codificação manual

No tratamento manual, o participante deverá resolver a tarefa sem utilizar assistentes de Inteligência Artificial.

Será permitido utilizar:

- IDE;
- documentação oficial do Python;
- documentação oficial das bibliotecas utilizadas;
- execução dos testes;
- ferramentas normais de desenvolvimento.

Não será permitido utilizar:

- ChatGPT;
- GitHub Copilot;
- Claude;
- Gemini;
- outras ferramentas de geração ou assistência de código por IA.

---

## T2 — Codificação com IA

No tratamento IA, o participante poderá utilizar o ChatGPT como assistente durante toda a resolução da tarefa.

Será permitido:

- realizar perguntas;
- solicitar explicações;
- solicitar exemplos;
- solicitar código;
- solicitar correções;
- solicitar sugestões de implementação;
- adaptar as respostas recebidas ao projeto.

O participante continuará sendo responsável pela implementação e pela integração do código ao projeto.

---

# 7. Objetos experimentais

Serão utilizadas **6 katas autorais**, desenvolvidas especificamente para o experimento.

A escolha por tarefas autorais tem como objetivo reduzir a ameaça de memorização das soluções por modelos de IA.

As katas deverão:

- ser implementadas em Python;
- possuir testes automatizados;
- apresentar dificuldade equivalente;
- possuir tamanho semelhante;
- utilizar conceitos de programação semelhantes;
- possuir regras específicas;
- ser suficientemente pequenas para serem resolvidas em até 35 minutos.

## Conjunto planejado

| Kata | Descrição | Principais conceitos |
|---|---|---|
| K1 | Validador de sequência | Strings, listas e condicionais |
| K2 | Agrupador de transações | Listas, filtros e agregação |
| K3 | Analisador de estoque | Listas, ordenação e regras de negócio |
| K4 | Calculadora de tarifas | Condicionais e regras de negócio |
| K5 | Processador de pedidos | Classes, listas e validações |
| K6 | Classificador de registros | Listas, filtros e agrupamentos |

As tarefas serão submetidas a um teste piloto para verificar se possuem dificuldade comparável.

---

# 8. Projeto experimental

Será utilizado o desenho:

**Crossover within-subject contrabalanceado.**

Cada participante realizará todas as seis tarefas.

Cada participante realizará:

- 3 tarefas com IA;
- 3 tarefas sem IA.

Dessa maneira, o desempenho do mesmo participante poderá ser comparado entre os dois tratamentos.

Esse desenho reduz o impacto das diferenças individuais de conhecimento e habilidade de programação.

---

# 9. Participantes

O experimento será realizado pelos **3 integrantes do grupo**.

Cada participante realizará seis trials:

**6 katas × 1 execução = 6 trials por participante.**

Portanto:

**3 participantes × 6 trials = 18 trials.**

Distribuição:

- 9 trials com IA;
- 9 trials sem IA.

---

# 10. Contrabalanceamento

Para reduzir o efeito da ordem dos tratamentos, a utilização de IA será alternada entre os participantes.

| Participante | K1 | K2 | K3 | K4 | K5 | K6 |
|---|---|---|---|---|---|---|
| Ana Luiza | IA | Manual | IA | Manual | IA | Manual |
| Bruna | Manual | IA | Manual | IA | Manual | IA |
| Walter | IA | Manual | IA | Manual | IA | Manual |

A ordem das tarefas será definida previamente e mantida durante o experimento.

---

# 11. Quantidade de medições

Para cada trial serão coletadas as seguintes informações:

| Métrica | Descrição |
|---|---|
| Participante | Identificador do participante |
| Kata | Identificação da tarefa |
| Tratamento | IA ou Manual |
| Tempo | Tempo em segundos |
| Testes totais | Quantidade total de testes |
| Testes passando | Testes aprovados |
| Testes falhando | Testes não aprovados |
| Taxa de sucesso | Percentual de testes aprovados |
| Complexidade | Complexidade ciclomática |
| Duplicação | Percentual de código duplicado |
| LOC | Linhas de código |
| Prompts | Número de interações com IA |

---

# 12. Procedimento de execução

Cada trial seguirá as seguintes etapas.

### 12.1 Preparação

O participante receberá:

- projeto da kata;
- descrição da tarefa;
- testes automatizados;
- ambiente previamente configurado.

### 12.2 Início

O cronômetro será iniciado no momento em que o participante iniciar a resolução.

### 12.3 Desenvolvimento

O participante desenvolverá a solução de acordo com o tratamento definido.

### 12.4 Execução dos testes

O participante poderá executar os testes durante todo o trial.

### 12.5 Encerramento

O trial será encerrado quando:

1. todos os testes forem aprovados; ou
2. o limite de 35 minutos for atingido.

### 12.6 Registro

Ao final serão registrados:

- tempo;
- testes aprovados;
- testes falhos;
- taxa de sucesso;
- código final.

### 12.7 Análise estática

O código final será analisado utilizando:

- Radon;
- jscpd.

---

# 13. Time-box

Cada trial terá duração máxima de:

**35 minutos.**

O mesmo limite será aplicado a todos os participantes e todas as katas.

Caso o participante atinja o limite sem concluir a tarefa, o desenvolvimento será interrompido e o estado atual do código será utilizado para a coleta das métricas.

O trial não será descartado.

---

# 14. Ambiente experimental

O ambiente será padronizado para todos os participantes.

### Linguagem

**Python 3.x**

A versão exata utilizada será registrada antes da execução.

### Testes

**pytest**

### Complexidade ciclomática

**Radon**

### Duplicação

**jscpd**

### Análise estatística

**Python + Pandas + SciPy**

### Visualização

**Matplotlib**

### Assistente de IA

**ChatGPT**

### Versionamento

**Git + GitHub**

### Gerenciamento do experimento

**GitHub Projects**

---

# 15. Ferramentas de análise estática

## 15.1 Radon

O Radon será utilizado para obter métricas relacionadas à estrutura do código Python.

Será utilizado principalmente para:

- complexidade ciclomática;
- linhas de código;
- Maintainability Index, caso o grupo decida utilizar essa métrica exploratória.

A complexidade ciclomática será utilizada como métrica principal da RQ3.

---

## 15.2 jscpd

O jscpd será utilizado para identificar trechos duplicados no código produzido pelos participantes.

Será registrada a porcentagem de código duplicado identificada pela ferramenta.

---

# 16. Estrutura de armazenamento dos dados

Os resultados serão armazenados em formato CSV.

Exemplo:

```text
participante,kata,tratamento,tempo_segundos,testes_total,testes_passando,testes_falhando,taxa_sucesso,complexidade_media,duplicacao_percentual,loc,prompts
P1,K1,IA,850,10,10,0,100,3.2,0,42,5
P1,K2,Manual,1240,8,6,2,75,4.1,2.5,38,0
```

O formato CSV facilitará a utilização posterior do **Pandas** para análise estatística e criação do dashboard.

---

# 17. Scripts da Sprint 01

Durante a Sprint 01 serão preparados scripts para automatizar a coleta das informações.

## 17.1 Script de cronometragem

O script será responsável por:

- iniciar o cronômetro;
- controlar o limite de 35 minutos;
- identificar o trial;
- registrar o tempo;
- armazenar os dados da execução.

## 17.2 Script de métricas

Será desenvolvido um script para executar as ferramentas de análise estática sobre o código final.

O script deverá coletar:

- complexidade ciclomática;
- LOC;
- duplicação.

A automatização busca garantir que todos os trials sejam avaliados utilizando o mesmo procedimento.

---

# 18. Ameaças à validade

## 18.1 Efeito de aprendizado

O participante pode melhorar seu desempenho ao longo do experimento por se familiarizar com o procedimento.

**Mitigação:** utilizar desenho crossover within-subject contrabalanceado e tarefas diferentes.

---

## 18.2 Familiaridade prévia com IA

Participantes que já possuem experiência com ferramentas de IA podem apresentar maior facilidade no tratamento IA.

**Mitigação:** registrar previamente a experiência dos participantes com assistentes de IA e considerar essa variável na discussão dos resultados.

---

## 18.3 Familiaridade com as tarefas

Um participante pode conhecer previamente uma tarefa ou solução semelhante.

**Mitigação:** utilizar katas autorais e pouco indexadas.

---

## 18.4 Memorização das soluções pela IA

Modelos de IA podem apresentar soluções semelhantes às disponíveis publicamente ou presentes em problemas conhecidos.

**Mitigação:** utilizar tarefas autorais, com regras específicas e que não tenham sido previamente publicadas pelo grupo.

---

## 18.5 Diferença de dificuldade entre katas

Uma kata pode ser naturalmente mais fácil ou mais difícil que outra.

**Mitigação:** utilizar tarefas com conceitos, tamanho e quantidade de testes semelhantes e realizar um teste piloto antes da execução oficial.

---

## 18.6 Diferença de habilidade entre participantes

Os participantes podem possuir diferentes níveis de conhecimento em programação.

**Mitigação:** desenho within-subject, no qual todos os participantes realizam tarefas nos dois tratamentos.

---

## 18.7 Influência específica da ferramenta

Os resultados podem depender das características do ChatGPT utilizado.

**Mitigação:** utilizar o mesmo assistente durante todos os trials com IA e registrar o modelo utilizado.

---

## 18.8 Limite de tempo

O limite de 35 minutos pode impedir a conclusão de determinadas tarefas.

**Mitigação:** registrar esses trials como 35 minutos, mantendo também a quantidade de testes aprovados no momento do encerramento.

---

# 19. Análise planejada

Devido ao tamanho reduzido da amostra e ao desenho within-subject, serão utilizadas estatísticas robustas.

Para a análise descritiva serão utilizadas:

- mediana;
- intervalo interquartil (IQR);
- mínimo;
- máximo.

Para a análise inferencial será utilizado o:

**teste de Wilcoxon para amostras pareadas.**

O teste será utilizado para comparar os tratamentos IA e Manual.

As análises serão realizadas para:

- RQ1 — tempo;
- RQ2 — taxa de sucesso;
- RQ3 — complexidade ciclomática;
- RQ3 — duplicação;
- RQ3 — LOC.

Será adotado nível de significância:

**α = 0,05.**

---

# 20. Critérios para avaliação das RQs

## RQ1

A hipótese de que o uso de IA reduz o tempo será apoiada caso:

1. o tratamento IA apresente menor mediana de tempo; e
2. o teste de Wilcoxon indique diferença estatisticamente significativa.

## RQ2

A hipótese de que o uso de IA melhora a qualidade funcional será apoiada caso:

1. o tratamento IA apresente maior mediana de taxa de sucesso; e
2. seja identificada diferença estatisticamente significativa.

## RQ3

Serão comparadas as distribuições das métricas de:

- complexidade ciclomática;
- duplicação;
- LOC.

A interpretação será realizada considerando o conjunto das métricas, evitando conclusões baseadas em apenas uma métrica estrutural.

---



Ao final da Sprint 01, o grupo deverá possuir:

- [ ] desenho experimental documentado;
- [ ] hipóteses definidas;
- [ ] variáveis definidas;
- [ ] tratamentos definidos;
- [ ] seis katas definidas;
- [ ] testes automatizados;
- [ ] ambiente Python configurado;
- [ ] assistente de IA definido;
- [ ] Radon configurado;
- [ ] jscpd configurado;
- [ ] script de cronometragem;
- [ ] script de métricas;
- [ ] estrutura de armazenamento dos dados;
- [ ] GitHub Projects atualizado;
- [ ] Issues atribuídas aos integrantes;
- [ ] commits vinculados às respectivas Issues.

Com esses artefatos, o experimento estará preparado para a execução dos trials durante a Sprint 02.