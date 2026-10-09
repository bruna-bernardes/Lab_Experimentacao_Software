# Laboratório 03 — Mineração de Métricas DORA

**Disciplina:** Laboratório de Experimentação de Software  
**Professor:** Danilo Maia  
**Grupo:** Ana, Bruna e Walter

## Objetivo

Minerar métricas DORA a partir de repositórios públicos do GitHub que utilizam GitHub Actions, investigando o desempenho de entrega de software.

## Sprint 1 — Lab03S01

A primeira sprint contempla a implementação de um pipeline de coleta para 100 repositórios elegíveis, com testes automatizados, cache, retomada e integração contínua.

## Estrutura

- `pipeline/selecao.py`: seleção dos repositórios e metadados.
- `pipeline/releases.py`: coleta de releases e commits.
- `pipeline/workflows.py`: coleta de execuções do GitHub Actions.
- `pipeline/api.py`: comunicação com a API, cache e rate limit.
- `metricas.py`: cálculos das métricas DORA.
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

No arquivo `config.json`, configure a janela de observação, a quantidade desejada de repositórios elegíveis e o número máximo de candidatos examinados.

**Atenção:** as datas atualmente utilizadas são provisórias. A coleta oficial deverá utilizar os 12 meses definidos pelo professor.

## Execução

Execute o pipeline com um único comando:

```powershell
python -m pipeline --config config.json
```

O pipeline realiza a seleção, coleta releases e workflow runs, calcula as métricas implementadas e gera arquivos CSV e JSON.

## Critérios de seleção

- Repositórios populares com mais de 1.000 estrelas.
- Utilização do GitHub Actions.
- Pelo menos 5 releases válidas na janela.
- Pelo menos 50 workflow runs válidos na branch principal, disparados por `push`.

## Resultados

Os resultados ficam na pasta `dados/`, incluindo:

- `repositorios_selecionados.csv`: metadados e métricas.
- `funil_selecao.csv`: contagens das etapas de seleção.
- `detalhes/`: dados coletados dos repositórios.
- `progresso/`: registros utilizados para retomada.

As pastas referentes às janelas de observação são identificadas automaticamente.

## Testes automatizados

```powershell
python -m pytest tests/ --cov=metricas --cov-report=term-missing --cov-fail-under=80
```

Na validação local da implementação inicial, foram aprovados 18 testes, com cobertura de 97,01% do módulo `metricas.py`.

## Integração contínua

O workflow `.github/workflows/lab03-testes.yml`, localizado na raiz do repositório, está configurado para executar os testes quando ocorrerem alterações no Laboratório 03.

A execução no GitHub Actions deverá ser verificada após os commits.

## Responsabilidades

- **Bruna:** seleção de repositórios, metadados e funil.
- **Ana:** coleta de releases, commits e cálculo de lead time.
- **Walter:** coleta de workflow runs, cache, tratamento de erros, CFR por CI e recuperação.

## Limitações

As métricas são aproximações obtidas de dados públicos do GitHub. Uma release não representa necessariamente um deploy em produção, assim como uma falha de CI não representa necessariamente uma falha em produção.

A validação completa, a ampliação da amostra e as análises estatísticas serão desenvolvidas nas próximas etapas do laboratório.