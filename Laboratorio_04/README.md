# LAB04 — Testes de Hipótese por Dentro

**Disciplina:** Laboratório de Experimentação de Software — PUC Minas  
**Sprint:** Lab04S01 (Sprint 1)  
**Equipe:** Bruna, Ana e Walter  
**Par escolhido (P4):** Teste Z para uma proporção × teste binomial exato

**Links:** [Repositório](https://github.com/bruna-bernardes/Lab_Experimentacao_Software) · [GitHub Projects](https://github.com/users/bruna-bernardes/projects/2/views/1)

## 1. Objetivo da Sprint 1

Investigar como dois testes de hipótese se comportam ao avaliar a taxa de falhas de execuções de integração contínua (CI). Nesta sprint, o projeto apresenta dados reais, define o cenário e as hipóteses, gera dados simulados, aplica os dois testes a um conjunto simulado e exibe os gráficos **G1** e **G2** em um dashboard Streamlit.

As simulações de 10.000 repetições, as análises de erro tipo I e poder estatístico e os gráficos **G3** e **G4** pertencem à **Sprint 2**.

## 2. Cenário e hipóteses

**Pergunta de pesquisa:** a proporção de execuções de CI com falha em um repositório público difere da meta de 5%?

- **H₀:** p = 0,05 — a proporção populacional de falhas é de 5%.
- **H₁:** p ≠ 0,05 — a proporção populacional de falhas é diferente de 5%.
- **Nível de significância:** α = 0,05.
- **Tipo de teste:** bicaudal, pois se investigam desvios tanto abaixo quanto acima de 5%.

Cada execução é representada por uma variável binária: `0` para sucesso e `1` para falha.

## 3. Coleta de dados reais

**Fonte:** GitHub Actions do repositório público [`pallets/flask`](https://github.com/pallets/flask/actions), obtidos pela API REST do GitHub (`/repos/{owner}/{repo}/actions/runs`).

**Critérios:** o script considera execuções com conclusão `success` ou `failure` e ignora conclusões como `cancelled` e `skipped`. As observações são execuções de workflows, e não necessariamente builds independentes.

**Amostra coletada:**

| Indicador | Resultado |
|---|---:|
| Execuções válidas | 100 |
| Sucessos | 91 |
| Falhas | 9 |
| Proporção observada de falhas | 9,0% |
| Meta de referência | 5,0% |

O arquivo `dados/execucoes_ci.csv` contém os registros reais, com identificador da execução, repositório, conclusão, indicador binário de falha, data e URL de origem. Os registros dessa amostra abrangem execuções de setembro a novembro de 2026. **Não são dados simulados.**

A diferença observada entre 9% e 5% não determina, por si só, significância estatística.

> **Reprodutibilidade:** o CSV coletado deve ser versionado no GitHub pelo **Walter** (Issue #64). Uma nova execução do comando de coleta pode produzir amostra diferente, pois o GitHub Actions continua recebendo execuções.

## 4. Modelo de simulação e expectativa anterior

A simulação representa `n = 100` execuções por meio de sorteios Bernoulli independentes, com taxa de falha estimada a partir dos dados reais (`p = 0,09`). O número total de falhas segue uma distribuição binomial. O código utiliza semente fixa para tornar os resultados reproduzíveis.

**Expectativa antes da simulação:** o teste binomial exato tende a controlar melhor o erro tipo I quando a amostra é pequena ou quando o número esperado de falhas sob H₀ (`n × 0,05`) é baixo. Já o teste Z depende de uma aproximação normal, que pode ser inadequada nessas condições. Esta expectativa será avaliada sistematicamente na Sprint 2; não constitui uma conclusão antecipada.

## 5. Testes estatísticos

- **Teste Z para uma proporção:** compara a proporção observada ao valor de referência usando aproximação normal.
- **Teste binomial exato:** calcula o p-valor diretamente a partir da distribuição binomial, sem depender da aproximação normal.

Ambos são aplicados ao **mesmo conjunto de dados simulados**, adotando α = 0,05. Se `p-valor < 0,05`, rejeita-se H₀; caso contrário, não há evidências suficientes para rejeitá-la. Não rejeitar H₀ **não** significa provar que ela é verdadeira.

**Exemplo exibido no dashboard durante a verificação local:** 1 falha em 100 execuções simuladas sob H₀; teste Z: `p ≈ 0,0665`; binomial exato: `p ≈ 0,0653`. Ambos não rejeitam H₀ nesse exemplo. Esses resultados pertencem à **simulação**, não à amostra real de 9 falhas.

## 6. Visualizações da Sprint 1

- **G1 — Dados reais × simulados:** compara as frequências de sucesso (`0`) e falha (`1`) no conjunto real e no conjunto simulado. Como as observações são binárias, utiliza gráficos de barras de frequências, equivalentes à representação de um histograma com duas categorias discretas.
- **G2 — Distribuições dos testes sob H₀:** apresenta a aproximação normal do teste Z e a distribuição discreta do teste binomial, incluindo regiões críticas e as áreas correspondentes aos p-valores de um exemplo.

Os gráficos contêm títulos, eixos, legendas e textos interpretativos no dashboard. O dashboard atual é a entrega parcial da Sprint 1; novas seções serão incluídas nas sprints seguintes.

## 7. Estrutura dos arquivos

```text
Laboratorio_04/
├── app.py                    # Dashboard Streamlit (G1 e G2)
├── README.md                 # Documentação e execução
├── requirements.txt          # Dependências Python
├── dados/
│   └── execucoes_ci.csv     # Amostra real de execuções de CI
└── src/
    ├── __init__.py
    ├── coleta.py             # Coleta de execuções via GitHub API
    └── estatistica.py        # Simulação e testes de hipótese
```

Os diretórios locais `.venv/` e `__pycache__/` **não devem ser commitados**.

## 8. Como executar (Windows / PowerShell)

Na raiz do repositório `Lab_Experimentacao_Software`:

```powershell
cd Laboratorio_04
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Com o CSV versionado em `dados/execucoes_ci.csv`, inicie o dashboard com **um único comando**:

```powershell
streamlit run app.py
```

O aplicativo normalmente estará disponível em `http://localhost:8501`.

**Para atualizar a amostra real, opcionalmente execute:**

```powershell
python -m src.coleta --repo pallets/flask --n 100
```

A coleta requer acesso à API pública do GitHub e pode estar sujeita a limites de requisições. Se necessário, configure a variável de ambiente `GITHUB_TOKEN` antes de executá-la. **Não é necessário repetir a coleta para visualizar o dashboard se o CSV já estiver presente.**

## 9. Limitações e cuidados metodológicos

- A amostra representa apenas um repositório e não permite generalização automática para todos os projetos de software.
- Execuções de workflows podem ser dependentes entre si, contrariando a hipótese simplificadora de independência do modelo Bernoulli.
- Excluir execuções canceladas ou inconclusivas pode influenciar a taxa observada.
- O teste Z pode ter aproximação insatisfatória com proporções próximas de zero e poucos eventos esperados.
- Um p-valor não informa a probabilidade de H₀ ser verdadeira, nem mede sozinho a relevância prática de uma diferença.

## 10. Divisão das Issues e commits

| Integrante | Issue | Responsabilidade | Arquivos principais |
|---|---|---|---|
| **Bruna** | [#63](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/63) | Simulação, testes estatísticos, estrutura, documentação e integração | `src/estatistica.py`, `src/__init__.py`, `requirements.txt`, `README.md` |
| **Walter** | [#64](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/64) | Coleta e preparação dos dados reais | `src/coleta.py`, `dados/execucoes_ci.csv` |
| **Ana** | [#65](https://github.com/bruna-bernardes/Lab_Experimentacao_Software/issues/65) | Dashboard, gráficos G1 e G2 e interpretações | `app.py` |

Cada integrante deve ser o **Assignee** de sua Issue e realizar seu commit usando a própria identidade Git. As mensagens devem referenciar a Issue correspondente:

```bash
# Bruna
git commit -m "feat: implementar simulacao e testes estatisticos refs #63"
# Walter
git commit -m "feat: implementar coleta de dados reais refs #64"
# Ana
git commit -m "feat: implementar dashboard com graficos G1 e G2 refs #65"
```

Os arquivos devem ser adicionados seletivamente (`git add <caminhos>`) para que um commit não inclua, por engano, arquivos de outro integrante. O GitHub Projects deve refletir o andamento das atividades.

## 11. Próximas etapas — Sprint 2

- **Q1:** estimar erro tipo I com 10.000 simulações sob H₀.
- **Q2:** estimar poder estatístico para pelo menos cinco tamanhos de efeito, começando em zero.
- **Q3:** repetir as análises em uma situação com violação de pressupostos.
- **G3:** comparar erro tipo I por teste e situação, com referência em 5%.
- **G4:** apresentar curvas de poder dos testes por tamanho de efeito.

Essas implementações não fazem parte da entrega da Sprint 1.
