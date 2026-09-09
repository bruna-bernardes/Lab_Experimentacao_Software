# Lab02 — Desenho do Experimento

## 1. Objetivo

Analisar o uso de um assistente de IA generativa na resolução de tarefas de programação, comparando seu efeito em relação à codificação manual quanto ao tempo de resolução, à qualidade funcional e à qualidade estrutural do código produzido.

O experimento será conduzido com três estudantes de graduação, utilizando quatro katas de dificuldade comparável, sob desenho crossover/within-subject e limite máximo de 35 minutos por trial.

## 2. Questões de Pesquisa

- **RQ1:** O uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação?
- **RQ2:** O uso de assistente de IA reduz a quantidade de defeitos (testes que falham) no código produzido?
- **RQ3:** O uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido?

## 3. Hipóteses

### RQ1 — Tempo

- **H0₁:** o uso de assistente de IA não reduz o tempo necessário para concluir as tarefas de programação.
- **H1₁:** o uso de assistente de IA reduz o tempo necessário para concluir as tarefas de programação.

### RQ2 — Defeitos

- **H0₂:** o uso de assistente de IA não reduz a quantidade de defeitos ao final dos trials.
- **H1₂:** o uso de assistente de IA reduz a quantidade de defeitos ao final dos trials.

### RQ3 — Estrutura do código

- **H0₃:** o uso de assistente de IA não altera significativamente a complexidade ciclomática nem a duplicação do código produzido.
- **H1₃:** o uso de assistente de IA altera significativamente a complexidade ciclomática e/ou a duplicação do código produzido.

## 4. Variáveis

### 4.1 Variável independente

Uso do assistente de IA durante a resolução da tarefa.

Valores possíveis:

- `COM_IA`
- `SEM_IA`

### 4.2 Variáveis dependentes

#### RQ1

- Tempo até todos os testes de aceitação passarem (`time-to-green`).
- Unidade principal: segundos.
- Trials que não forem concluídos dentro do limite serão registrados como **censurados em 2100 segundos (35 minutos)**.

#### RQ2

- Quantidade de testes passando ao final do trial.
- Quantidade de testes falhando ao final do trial.
- Taxa de sucesso dos testes:

  `testes passando / total de testes × 100`

#### RQ3

- Complexidade ciclomática média por função/método.
- Percentual de linhas duplicadas.
- LOC como métrica de controle.

## 5. Métricas selecionadas e justificativa

### RQ1

A métrica principal será o **time-to-green**, pois mede diretamente quanto tempo o participante leva para produzir uma solução que satisfaz todos os testes de aceitação.

Como o número de observações é pequeno e o tempo pode apresentar valores extremos, a análise descritiva utilizará **mediana e IQR**, em vez de média e desvio-padrão.

Trials não concluídos serão mantidos na análise como censurados em 35 minutos, evitando favorecer artificialmente o tratamento com maior quantidade de falhas.

### RQ2

A métrica principal será a **taxa de sucesso dos testes de aceitação**, pois permite comparar katas mesmo que exista diferença no número absoluto de testes.

Como medida complementar será registrado o **número absoluto de testes falhando** ao final do time-box.

### RQ3

Serão utilizadas:

- **Complexidade ciclomática média**, coletada com Radon;
- **Duplicação percentual**, coletada com jscpd;
- **LOC**, utilizada como métrica de controle.

A utilização de LOC ajuda a interpretar complexidade e duplicação, pois soluções mais extensas podem apresentar valores absolutos maiores apenas por serem mais verbosas.

## 6. Tratamentos

### Tratamento A — COM_IA

O participante poderá utilizar o assistente de IA definido pelo grupo durante todo o trial.

O grupo deverá utilizar o mesmo assistente de IA e a mesma configuração em todos os trials.

- **Assistente:** GitHub Copilot
- **Ambiente:** Visual Studio Code
- **Modelo/versão:** Auto

### Tratamento B — SEM_IA

O participante deverá resolver a tarefa sem utilizar assistentes de IA generativa.

Durante esses trials não será permitido utilizar ChatGPT, GitHub Copilot, Claude, Gemini ou ferramentas equivalentes para obter sugestões de implementação.

## 7. Objetos experimentais

Serão utilizados quatro katas em Python, de dificuldade comparável e preferencialmente autorais ou pouco indexados.

Objetos experimentais:

1. **Kata 01 — Tarifa de Entrega**
2. **Kata 02 — Cobrança de Estacionamento**
3. **Kata 03 — Processamento de Pedidos**
4. **Kata 04 — Classificação de Chamados por SLA**

Critérios para equivalência:

- quantidade semelhante de regras de negócio;
- interfaces de entrada e saída simples;
- aproximadamente o mesmo número de testes de aceitação;
- nenhuma dependência externa;
- solução esperada compatível com o limite de 35 minutos;
- evitar problemas clássicos amplamente indexados;
- evitar que um kata reutilize diretamente a solução de outro.

Cada kata deverá possuir:

- enunciado próprio;
- arquivo inicial de implementação;
- testes automatizados de aceitação;
- critérios objetivos para determinar sucesso.

## 8. Tipo de projeto experimental

Será utilizado um desenho **crossover/within-subject contrabalanceado**.

Cada participante realizará os quatro katas, sendo:

- 2 trials `COM_IA`;
- 2 trials `SEM_IA`.

Assim, cada participante atua como seu próprio controle, reduzindo a influência de diferenças individuais de habilidade.

## 9. Participantes

- Bruna
- Ana
- Walter

## 10. Quantidade de medições

O experimento produzirá:

- 3 participantes;
- 4 trials por participante;
- 12 trials no total;
- 6 trials `COM_IA`;
- 6 trials `SEM_IA`.

Cada trial terá limite máximo de **35 minutos**.

## 11. Contrabalanceamento

O plano será gerado pelo script `scripts/gerar_plano_trials.py`.

Distribuição definida:

| Participante | Kata 01 | Kata 02 | Kata 03 | Kata 04 |
|---|---|---|---|---|
| Bruna | COM_IA | SEM_IA | SEM_IA | COM_IA |
| Ana | SEM_IA | COM_IA | COM_IA | SEM_IA |
| Walter | SEM_IA | COM_IA | SEM_IA | COM_IA |

A ordem de execução também será diferente entre os participantes para reduzir efeitos de ordem e fadiga.

## 12. Ambiente experimental

- **Linguagem:** Python
- **IDE:** Visual Studio Code
- **Testes automatizados:** pytest
- **Medição de complexidade/LOC:** Radon
- **Duplicação:** jscpd
- **Cronometragem/coleta:** script próprio do grupo
- **Sistema operacional:** Windows
- **Time-box:** 35 minutos

Versões já validadas no ambiente do grupo:

- pytest: 9.1.1
- Radon: 6.0.1

Também serão registradas as versões de:

- Python;
- Visual Studio Code;
- jscpd;
- GitHub Copilot.

## 13. Procedimento resumido

1. Preparar o ambiente antes do início do trial.
2. Confirmar o participante, kata e tratamento.
3. Iniciar o script de cronometragem.
4. Resolver o kata respeitando o tratamento definido.
5. Encerrar automaticamente quando todos os testes passarem ou ao atingir 35 minutos.
6. Registrar tempo, censura, testes passando, testes falhando e taxa de sucesso.
7. Executar as métricas estáticas sobre o código final.
8. Não alterar a solução após o encerramento do trial.
9. Armazenar os dados para posterior análise estatística.

## 14. Análise prevista

A análise descritiva utilizará principalmente:

- mediana;
- IQR;
- gráficos comparando `COM_IA` e `SEM_IA`.

Para análise inferencial será utilizado o **teste de Wilcoxon para amostras pareadas**, consistente com o desenho within-subject e com o pequeno tamanho da amostra.

## 15. Ameaças à validade e mitigação

### Diferenças de habilidade entre participantes

**Ameaça:** participantes podem possuir níveis diferentes de experiência em programação.

**Mitigação:** utilização de desenho within-subject, em que todos realizam trials nos dois tratamentos.

### Efeito de aprendizado

**Ameaça:** resolver um kata pode ajudar indiretamente na resolução dos seguintes.

**Mitigação:** utilização de katas diferentes e contrabalanceamento da ordem.

### Familiaridade com IA

**Ameaça:** participantes podem ter níveis diferentes de experiência com ferramentas de IA.

**Mitigação:** uso do mesmo assistente e da mesma configuração em todos os trials.

### Memorização

**Ameaça:** um assistente pode reproduzir soluções conhecidas de problemas muito populares.

**Mitigação:** preferência por katas autorais ou pouco indexados e rejeição de exercícios clássicos amplamente conhecidos.

### Vazamento de solução

**Ameaça:** participantes podem conhecer previamente a solução produzida por outro integrante.

**Mitigação:** não compartilhar implementações ou prompts antes que todos concluam seus trials.

### Efeito de ordem e fadiga

**Ameaça:** trials executados mais tarde podem sofrer influência de cansaço ou prática acumulada.

**Mitigação:** ordens diferentes entre os participantes.

### Variação do modelo de IA

**Ameaça:** o GitHub Copilot será utilizado com seleção automática de modelo (`Auto`), podendo utilizar modelos diferentes entre as interações.

**Mitigação:** utilizar a mesma configuração do GitHub Copilot para todos os participantes e realizar os trials em um intervalo curto de tempo.

### Equivalência dos katas

**Ameaça:** diferenças reais de dificuldade podem afetar o tempo e a taxa de sucesso.

**Mitigação:** manter quantidade semelhante de regras, testes e esforço estimado e revisar os quatro katas antes da execução.

### Instrumentação

**Ameaça:** erros nos scripts de cronometragem ou métricas podem comprometer os dados.

**Mitigação:** validar os scripts com exemplos descartáveis antes dos trials oficiais.

### Tamanho reduzido da amostra

**Ameaça:** 12 trials oferecem baixo poder estatístico.

**Mitigação:** utilizar mediana, IQR, Wilcoxon e discutir explicitamente a limitação na validade externa.
