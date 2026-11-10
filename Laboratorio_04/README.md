# LAB04 — Testes de Hipótese por Dentro

**Disciplina:** Laboratório de Experimentação de Software — PUC Minas  
**Equipe:** Bruna, Ana e Walter  
**Par escolhido (P4):** Teste Z para uma proporção × teste binomial exato  
**Etapas implementadas:** Lab04S01 e Lab04S02; dashboard preparado para a entrega final

**Links:** [Repositório](https://github.com/bruna-bernardes/Lab_Experimentacao_Software) · [GitHub Projects](https://github.com/users/bruna-bernardes/projects/2/views/1)

## 1. Objetivo e entregas

Investigar como os testes Z para uma proporção e binomial exato se comportam ao avaliar a proporção de falhas de execuções de integração contínua (CI) de um projeto open-source. Dados reais fundamentam o cenário; simulações de Monte Carlo permitem conhecer a proporção verdadeira de falhas e estimar erro tipo I e poder estatístico.

- **Sprint 1 (Lab04S01):** coleta real, cenário, hipóteses, geração de dados binários, aplicação dos testes e gráficos G1/G2.
- **Sprint 2 (Lab04S02):** Q1 (erro tipo I), Q2 (poder), Q3 (amostra pequena) e gráficos G3/G4.
- **Entrega final:** dashboard completo com sete seções, tabela de resultados reais, recomendação e apresentação oral. A apresentação é uma etapa de avaliação separada da Sprint 2.

## 2. Cenário e hipóteses

**Pergunta de pesquisa:** a proporção de execuções de CI com falha no repositório analisado difere da meta de 5%?

- **H₀:** p = 0,05 (taxa populacional de falhas igual a 5%).
- **H₁:** p ≠ 0,05 (taxa populacional de falhas diferente de 5%).
- **Significância:** α = 0,05, com testes **bicaudais**.
- **Variável:** `falha = 0` para sucesso e `falha = 1` para falha.

O teste Z utiliza uma aproximação normal para a estatística da proporção; o binomial exato utiliza a distribuição binomial para calcular o p-valor. Em ambos, rejeitamos H₀ quando `p-valor < 0,05`.

**Expectativa estabelecida antes das simulações:** o teste binomial exato deve controlar melhor o erro tipo I quando o tamanho da amostra é pequeno e há poucas falhas esperadas; o teste Z pode ser liberal se a aproximação normal for inadequada.

## 3. Dados reais e rastreabilidade

**Origem:** [GitHub Actions do projeto `pallets/flask`](https://github.com/pallets/flask/actions), via API REST `/repos/{owner}/{repo}/actions/runs`.

O script `src/coleta.py` inclui apenas execuções com conclusão `success` ou `failure`; ignora execuções canceladas, puladas e outras conclusões. Os registros em `dados/execucoes_ci.csv` incluem identificador, data, link da execução, conclusão e indicador de falha. A amostra coletada vai de setembro a novembro de 2026.

| Indicador | Valor |
|---|---:|
| Execuções válidas | 100 |
| Sucessos | 91 |
| Falhas | 9 |
| Taxa de falha observada | 9,0% |
| Meta de referência | 5,0% |
| Diferença observada | +4,0 pontos percentuais |

**Atenção:** o CSV versionado é a amostra fixa utilizada no dashboard. Reexecutar a coleta posteriormente pode alterar a amostra, pois as execuções do GitHub continuam ocorrendo. A coleta é opcional para iniciar o dashboard.

## 4. Sprint 1 — Modelo e gráficos G1/G2

O exemplo da Sprint 1 simula 100 observações Bernoulli independentes com probabilidade `p = 0,09`, estimada dos dados coletados; o total de falhas segue distribuição binomial. Utiliza-se semente fixa para reprodutibilidade.

- **G1:** resumo percentual de sucesso/falha e histogramas discretos dos dados reais versus os simulados. O histograma tem dois valores possíveis, 0 e 1.
- **G2:** distribuição normal de referência do teste Z e distribuição binomial sob H₀, regiões críticas e áreas correspondentes ao p-valor de um exemplo simulado.

No exemplo fixo do G2, foi observada **1 falha em 100 execuções simuladas sob H₀**: `Z ≈ −1,835`, `p(Z) ≈ 0,0665` e `p(binomial exato) ≈ 0,0653`. Nenhum dos dois testes rejeita H₀ nesse exemplo. **Esse exemplo não é a aplicação aos dados reais.**

## 5. Sprint 2 — Simulações Q1, Q2 e Q3

O arquivo `src/simulacoes.py` implementa Monte Carlo reprodutível com `numpy.random.default_rng(42)` e **10.000 repetições por configuração**. São comparados os mesmos conjuntos de contagens binomiais nos dois testes, para permitir comparação justa.

**Situações:**

- **Amostra principal:** `n = 100`, tamanho da amostra real coletada, mas com *dados gerados por simulação*.
- **Amostra pequena:** `n = 20`, para investigar a violação das condições usuais da aproximação normal: sob H₀, `n × p₀ = 20 × 0,05 = 1` (inferior a 5).

**Tamanhos de efeito estudados:** diferenças acima da meta de 5% de `0, 1, 2, 3, 4, 5, 7 e 10 pontos percentuais`, ou seja, proporções verdadeiras `p = 0,05; 0,06; 0,07; 0,08; 0,09; 0,10; 0,12; 0,15`. Trata-se apenas de efeitos **positivos**; a hipótese estatística continua bicaudal.

- **Q1 — Erro tipo I:** quando o efeito é 0 e H₀ é verdadeira (`p = 0,05`), estimar a frequência de rejeições indevidas.
- **Q2 — Poder:** para efeitos acima de 0, estimar a frequência de rejeição de H₀ quando há diferença real da meta.
- **Q3 — Pressupostos:** repetir Q1 e Q2 para `n = 20` e comparar com `n = 100`.

### 5.1 Resultados reproduzidos

Os resultados abaixo foram obtidos na execução local documentada da Sprint 2 (10.000 repetições e semente fixa):

| Situação | Teste Z — erro tipo I | Binomial exato — erro tipo I |
|---|---:|---:|
| n = 100 | 3,58% | 3,58% |
| n = 20 | 7,77% | 1,60% |

| Taxa verdadeira de falhas | n = 100 — ambos os testes | n = 20 — Teste Z | n = 20 — Binomial exato |
|---|---:|---:|---:|
| 9% | 41,35% | 26,45% | 9,91% |
| 15% | 94,61% | 60,35% | 36,29% |

Para `n = 100`, os testes tiveram as mesmas **decisões de rejeição** nas configurações simuladas, embora seus p-valores não sejam necessariamente iguais. Para `n = 20`, o Z teve mais rejeições, porém seu erro tipo I de **7,77% ultrapassou α = 5%**; portanto, não se pode interpretar sua maior taxa de rejeição como vantagem inequívoca de desempenho. O binomial exato permaneceu conservador (1,60%).

### 5.2 Gráficos G3 e G4

- **G3 — Erro tipo I:** barras por teste e tamanho de amostra, com linha horizontal de referência em 5%.
- **G4 — Curvas de poder:** proporção de rejeições versus efeito (em pontos percentuais acima de 5%), com cores fixas por teste e estilo da linha distinguindo os tamanhos de amostra. No ponto de efeito zero, a taxa representa **erro tipo I**, não poder.

Todos os gráficos apresentam títulos, eixos, unidades, legendas e interpretações no dashboard.

## 6. Aplicação aos dados reais

O arquivo `src/analise_reais.py` aplica os testes à amostra observada (`9` falhas em `100` execuções), usando `src/estatistica.py`.

| Teste | Estatística | p-valor | Efeito observado | Decisão (α = 0,05) |
|---|---|---:|---:|---|
| Z para uma proporção | Z ≈ 1,835 | 0,0665 | +4,0 p.p. | Não rejeita H₀ |
| Binomial exato | k = 9/100 | 0,1002 | +4,0 p.p. | Não rejeita H₀ |

A taxa observada é maior do que a meta, mas **nenhum dos testes encontrou evidência suficiente para rejeitar H₀ a 5%**. Não rejeitar H₀ não prova que a taxa verdadeira é de 5%, e um p-valor não mede a probabilidade de H₀ ser verdadeira.

## 7. Conclusão e recomendação

A expectativa inicial foi sustentada no cenário de amostra pequena: o **binomial exato** controlou o erro tipo I, enquanto o **teste Z** ultrapassou o nível nominal. Na amostra principal com 100 execuções, ambos tiveram decisões equivalentes nas simulações feitas. A maior taxa de rejeições do Z em `n = 20` não pode ser analisada isoladamente, pois vem acompanhada de excesso de falsos positivos.

**Recomendação:** priorizar o **binomial exato** quando a taxa de referência é baixa e a amostra é pequena; considerar o Z quando a aproximação normal for adequada. A escolha depende dos pressupostos, e não apenas da curva de poder.

**Limitações:** apenas um repositório; possível dependência entre workflows; exclusão de execuções inconclusivas; simplificação de probabilidade constante; poderes simulados somente para aumentos da taxa de falhas; e variação Monte Carlo finita, apesar da semente fixa.

## 8. Organização do dashboard

O dashboard Streamlit apresenta as seções, nesta ordem:

1. Cenário, H₀/H₁ e origem da amostra.
2. Os dados — G1 (comparação real/simulada).
3. Como os testes funcionam — G2 (distribuições, regiões críticas, p-valores).
4. Erro tipo I — G3 (Q1 e Q3).
5. Poder estatístico — G4 (Q2 e Q3).
6. Dados reais — tabela com estatística, p-valor, efeito e conclusão.
7. Conclusão e recomendação.

## 9. Estrutura dos arquivos

```text
Laboratorio_04/
├── app.py                      # Dashboard Streamlit: G1 a G4 e seções finais
├── README.md                   # Documentação
├── requirements.txt            # Dependências
├── dados/
│   └── execucoes_ci.csv       # Amostra real coletada
├── snapshots/
│   └── Lab04S01.csv           # Snapshot da Sprint 1
└── src/
    ├── __init__.py
    ├── coleta.py               # GitHub Actions → CSV
    ├── estatistica.py          # Testes Z e binomial exato
    ├── simulacoes.py           # Monte Carlo: Q1, Q2 e Q3
    └── analise_reais.py        # Tabela estatística dos dados reais
```

O snapshot `Lab04S02.csv` será produzido quando o GitHub Projects da Sprint 2 estiver concluído. As pastas `.venv/` e `__pycache__/` não devem ser versionadas.

## 10. Instalação e execução (Windows / PowerShell)

Na raiz do repositório:

```powershell
cd Laboratorio_04
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Depois de instalar as dependências e com o CSV presente, execute o dashboard com um único comando:**

```powershell
python -m streamlit run app.py
```

Se o VS Code ativar o ambiente virtual de outro laboratório, chame diretamente o Python deste laboratório:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

A interface normalmente abre em `http://localhost:8501`. A execução local de 10.000 repetições poderá levar alguns instantes na primeira abertura; o dashboard usa cache para evitar recálculo desnecessário.

### Testes isolados dos módulos

**Simulações (Q1–Q3):**

```powershell
.\.venv\Scripts\python.exe -c "from src.simulacoes import executar_simulacoes; df = executar_simulacoes(100); print(df.to_string(index=False))"
```

**Testes dos dados reais:**

```powershell
.\.venv\Scripts\python.exe -c "import pandas as pd; from src.analise_reais import tabela_dados_reais; df = pd.read_csv('dados/execucoes_ci.csv'); print(tabela_dados_reais(df).to_string(index=False))"
```

**Coleta opcional de dados atualizados** (não necessária para abrir o dashboard):

```powershell
python -m src.coleta --repo pallets/flask --n 100
```

A coleta usa a API pública do GitHub e pode necessitar de `GITHUB_TOKEN` dependendo dos limites de requisições.

## 11. GitHub Projects, Issues e commits

### Sprint 1 — Concluída

| Integrante | Issue | Entrega |
|---|---|---|
| Bruna | [#63](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/63) | Testes, simulação inicial e documentação |
| Walter | [#64](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/64) | Coleta de dados reais e CSV |
| Ana | [#65](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/65) | Dashboard e gráficos G1/G2 |
| Bruna | [#66](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/66) | Snapshot do Project |

### Sprint 2 — Issues a criar

| Integrante | Issue | Entrega planejada |
|---|---|---|
| Bruna | A definir | `src/simulacoes.py`, Q1–Q3, documentação e integração |
| Ana | A definir | `app.py`, G3/G4 e integração visual das seções 6/7 |
| Walter | A definir | `src/analise_reais.py`, tabela de dados reais |

Cada integrante deve ser Assignee de ao menos uma Issue com **código commitado**, e o respectivo commit deve fazer referência ao **número real** da Issue. Não usar números de Issues provisórios nas mensagens de commit. Manter os cartões do GitHub Projects atualizados e respeitar o WIP.

### Snapshot da Sprint 2 (após concluir as Issues)

Na raiz do repositório:

```powershell
python scripts_comuns/exportar_snapshot_project.py --laboratorio Laboratorio_04 --sprint Lab04S02
```

O comando gera `Laboratorio_04/snapshots/Lab04S02.csv`. Conferir se as Issues e responsáveis corretos estão listados antes do commit.

## 12. Apresentação final

O dashboard apresenta os resultados para apoiar a discussão oral. A apresentação final deve cobrir cenário, hipóteses, escolha de testes, parâmetros, significado dos p-valores, Q1/Q2/Q3, pressupostos, resultados nos dados reais, recomendação e limitações. Conforme o enunciado, os integrantes dividem as perguntas, com **ao menos quatro respostas por integrante**. A entrega final e sua apresentação possuem avaliação separada da Sprint 2.
