# Laboratório 03 — Mineração de Métricas DORA

**Disciplina:** Laboratório de Experimentação de Software  
**Professor:** Danilo Maia  
**Grupo:** Ana, Bruna e Walter

## Objetivo

Minerar métricas DORA a partir de repositórios públicos do GitHub que utilizam GitHub Actions, investigando o desempenho de entrega de software.

## Sprint 1 — Lab03S01

A primeira sprint contempla a implementação de um pipeline de coleta para 100 repositórios elegíveis, com testes automatizados, cache, retomada e integração contínua.

## Sprint 2 — Lab03S02

A segunda sprint amplia a coleta para a amostra final (≥ 300 repositórios), calcula todas as variantes obrigatórias das métricas, gera o dataset final com dicionário de dados e executa a validação manual com uma amostra-ouro de 60 repositórios (kappa de Fleiss, consenso e precisão/recall/F1 da heurística de release corretiva). O planejamento está em `docs/sprint2/planejamento_sprint2.md`.

## Estrutura

- `pipeline/selecao.py`: seleção dos repositórios e metadados.
- `pipeline/releases.py`: coleta de releases e commits.
- `pipeline/workflows.py`: coleta de execuções do GitHub Actions.
- `pipeline/api.py`: comunicação com a API, cache e rate limit.
- `pipeline/config.py`: leitura do `config.json` e pastas de saída.
- `pipeline/exportar.py`: exportação offline dos dados coletados para `resultados/`.
- `pipeline/consolidar.py`: recálculo offline das métricas e `dataset_final.csv`.
- `pipeline/dicionario.py`: conferência e geração do dicionário de dados.
- `metricas.py`: cálculos das métricas DORA.
- `heuristica.py`: heurística de identificação de releases corretivas (CFR b).
- `validacao/`: amostra-ouro, rotulagem, kappa de Fleiss, consenso e avaliação da heurística.
- `tests/`: testes automatizados.
- `config.json`: configurações da coleta.
- `dados/`: resultados gerados pelo pipeline.

## Requisitos

- Python 3.13
- Token pessoal do GitHub
- Dependências presentes em `requirements.txt`

## Instalação

A partir da pasta `Laboratorio_03`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configuração

Defina o token do GitHub como variável de ambiente:

```powershell
$env:GITHUB_TOKEN="SEU_TOKEN"
```

No arquivo `config.json`, configure:

| Campo | Significado |
|---|---|
| `inicio`, `fim` | Janela de observação (12 meses fixados pelo professor) |
| `quantidade` | Elegíveis desejados (320 = margem sobre o mínimo de 300) |
| `maximo_candidatos` | Teto de candidatos examinados |
| `semente_amostragem` | Semente do embaralhamento do pool de candidatos |
| `versao_heuristica` | Versão de `heuristica.py` usada no CFR (b) |

**Atenção:** confirme a janela oficial antes da coleta completa. Mudar a janela depois cria outra pasta em `dados/` e exige coletar novamente as runs e as comparações.

## Execução

Execute o pipeline com um único comando:

```powershell
python -m pipeline --config config.json
```

O pipeline realiza a seleção, coleta releases e workflow runs, calcula as métricas implementadas e gera arquivos CSV e JSON. Se for interrompido (rate limit, queda de rede, `Ctrl+C`), basta rodar o mesmo comando: ele continua de onde parou, sem repetir chamadas já feitas.

### Etapas offline (sem token, sem rede)

```powershell
python -m pipeline.exportar   --config config.json   # resultados/: amostra, funil, releases, commits, runs
python -m pipeline.consolidar --config config.json   # resultados/dataset_final.csv
python -m pipeline.dicionario                        # confere e gera resultados/dicionario_dados.md
```

### Validação manual

```powershell
python -m validacao.amostra_ouro                     # sorteio (random_state=42) e planilhas em validacao/rotulos/
python -m validacao.concordancia --somente-validar   # confere os arquivos de rótulos
python -m validacao.concordancia                     # kappa de Fleiss → validacao/concordancia.csv
python -m validacao.consenso                         # consenso → validacao/consenso_*.csv
python -m validacao.avaliar_heuristica --todas       # P/R/F1 → validacao/heuristica_versoes.csv
python -m pipeline.consolidar --config config.json   # dataset final com consenso e heurística escolhida
```

## Critérios de seleção

- Repositórios populares com mais de 1.000 estrelas, não arquivados e que não são forks; o pool de todas as faixas é embaralhado com semente fixa (`docs/sprint2/decisao_amostragem.md`).
- Utilização do GitHub Actions.
- Pelo menos 5 releases válidas na janela.
- Pelo menos 50 workflow runs válidos na branch principal, disparados por `push`.

## Resultados

Os dados brutos ficam em `dados/` (não versionada):

- `pool_candidatos.json`: pool embaralhado, data da busca e semente.
- `repositorios_selecionados.csv` e `funil_selecao.csv`: acompanhamento da coleta.
- `detalhes/`: dados coletados dos repositórios elegíveis.
- `progresso/`: registros utilizados para retomada.
- `erros_coleta.json`: histórico cumulativo de erros.

Os arquivos versionados ficam em `resultados/` (`amostra_final.csv`, `funil_selecao.csv`, `releases_janela.csv`, `commits_releases.csv.gz`, `runs.csv.gz`, `dataset_final.csv`, `dicionario_dados.csv/.md`) e em `validacao/`. Cada coluna está descrita em `resultados/dicionario_dados.md`.

## Testes automatizados

```powershell
python -m pytest tests/ --cov=metricas --cov-report=term-missing --cov-fail-under=80
```

O número de testes e a cobertura de referência são os da última execução do GitHub Actions.

## Integração contínua

O workflow `.github/workflows/lab03-testes.yml`, localizado na raiz do repositório, está configurado para executar os testes quando ocorrerem alterações no Laboratório 03.

A execução no GitHub Actions deverá ser verificada após os commits.

## Responsabilidades

Sprint 1:

- **Bruna:** seleção de repositórios, metadados e funil.
- **Ana:** coleta de releases, commits e cálculo de lead time.
- **Walter:** coleta de workflow runs, cache, tratamento de erros, CFR por CI e recuperação.

Sprint 2:

- **Bruna:** estratégia de amostragem, amostra-ouro, kappa de Fleiss, consenso e integração.
- **Ana:** heurística de release corretiva, deployment frequency, CFR (b) e avaliação da heurística.
- **Walter:** pipeline da coleta ampliada, coleta completa, exportação, dataset final e dicionário de dados.
- **Os três:** rotulagem independente da amostra-ouro e seção de Metodologia.

## Limitações

As métricas são aproximações obtidas de dados públicos do GitHub. Uma release não representa necessariamente um deploy em produção, assim como uma falha de CI não representa necessariamente uma falha em produção.

A heurística de release corretiva é validada contra a amostra-ouro (`validacao/heuristica_versoes.csv`). As análises estatísticas das RQs são desenvolvidas na Sprint 3.