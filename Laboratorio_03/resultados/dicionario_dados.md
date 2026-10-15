# Dicionário de dados — Lab03

Gerado por `python -m pipeline.dicionario` a partir de `dicionario_dados.csv`. Não edite este arquivo à mão.


## `resultados/dataset_final.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | GET /search/repositories → full_name | identificador owner/nome | nunca |
| branch | texto | não se aplica | GET /repos/{o}/{r} → default_branch | valor copiado | nunca |
| estrelas | inteiro | contagem | GET /repos/{o}/{r} → stargazers_count | valor na data da coleta | nunca |
| linguagem | texto | não se aplica | GET /repos/{o}/{r} → language | valor copiado | repositório sem linguagem detectada |
| contribuidores | inteiro | contagem | GET /repos/{o}/{r}/contributors?per_page=1&anon=true → cabeçalho Link | número da última página (inclui anônimos) | API recusou listar (repositório muito grande) |
| idade_dias | inteiro | dias | GET /repos/{o}/{r} → created_at | fim da janela − created_at | nunca |
| releases_janela | inteiro | contagem | GET /repos/{o}/{r}/releases | releases com draft = false, prerelease = false e published_at na janela | nunca |
| deployment_frequency_semana | decimal | releases/semana | derivado | releases_janela ÷ (duração da janela em dias ÷ 7) | nunca |
| lead_time_release_horas | decimal | horas | GET /repos/{o}/{r}/compare/{anterior}...{R} → commit.author.date; release.published_at | mediana, entre as releases, de (published_at de R − commit.author.date mais antigo de R); valores negativos descartados | nenhuma release com commits e lead time ≥ 0 |
| lead_time_commit_horas | decimal | horas | idem | mediana, sobre todos os commits de todas as releases, de (published_at de R − commit.author.date); valores negativos descartados | nenhum commit com lead time ≥ 0 |
| releases_lead_time | inteiro | contagem | derivado | releases que contribuíram para a variante (a) | nunca |
| releases_ignoradas_primeira | inteiro | contagem | derivado | releases da janela que são a primeira release da história (sem release anterior) | nunca |
| releases_ignoradas_comparacao | inteiro | contagem | GET compare → HTTP 404/422 | releases com release anterior, mas sem comparação disponível (tag apagada ou reescrita) | nunca |
| releases_sem_commits | inteiro | contagem | derivado | releases com comparação disponível e zero commits | nunca |
| commits_lead_time_negativo | inteiro | contagem | derivado | commits com author.date posterior à publicação da release (rebase/squash); descartados | nunca |
| runs_sucesso | inteiro | contagem | GET /repos/{o}/{r}/actions/runs?branch=<default>&event=push → conclusion | runs com conclusion = success na janela | nunca |
| runs_falha | inteiro | contagem | idem | runs com conclusion ∈ {failure, timed_out, startup_failure} | nunca |
| cfr_ci | decimal | proporção (0–1) | derivado | runs_falha ÷ (runs_falha + runs_sucesso); demais conclusions ignoradas | sem runs válidas |
| releases_avaliadas_cfr_entrega | inteiro | contagem | derivado | releases da janela publicadas até 7 dias antes do fim | nunca |
| releases_falhas_cfr_entrega | inteiro | contagem | derivado + heurística | releases R cuja release seguinte R' sai em até 7 dias e é corretiva segundo a heurística | nunca |
| releases_censuradas_cfr_entrega | inteiro | contagem | derivado | releases publicadas nos últimos 7 dias da janela (fora do denominador) | nunca |
| cfr_entrega | decimal | proporção (0–1) | derivado | releases_falhas_cfr_entrega ÷ releases_avaliadas_cfr_entrega | nenhuma release avaliável |
| versao_heuristica | texto | não se aplica | config.json → versao_heuristica | versão de heuristica.py usada no CFR (b) | nunca |
| recuperacao_horas | decimal | horas | runs → run_started_at, updated_at, workflow_id | mediana dos episódios: updated_at do 1º sucesso − run_started_at da 1ª falha após um sucesso, por workflow | nenhum episódio encerrado |
| episodios_recuperados | inteiro | contagem | derivado | episódios de falha encerrados dentro da janela | nunca |
| episodios_censurados | inteiro | contagem | derivado | episódios de falha sem sucesso posterior na janela | nunca |
| proporcao_censura | decimal | proporção (0–1) | derivado | episodios_censurados ÷ (episodios_recuperados + episodios_censurados) | nenhum episódio |
| amostra_ouro | booleano | não se aplica | validacao/consenso_repositorios.csv | true se o repositório tem rótulo de consenso | nunca |
| tipo_projeto_consenso | categórico | não se aplica | rotulagem manual (consenso) | biblioteca_framework \| aplicacao_servico \| ferramenta_cli \| outro | repositório fora da amostra-ouro |
| entregas_reais_consenso | categórico | não se aplica | rotulagem manual (consenso) | sim \| nao \| incerto | repositório fora da amostra-ouro |

## `resultados/amostra_final.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | GET /search/repositories → full_name | repositório elegível (≥ 5 releases e ≥ 50 runs válidas na janela) | nunca |
| ordem_pool | inteiro | posição | pipeline | posição no pool embaralhado com semente fixa | nunca |
| branch | texto | não se aplica | GET /repos/{o}/{r} → default_branch | valor copiado | nunca |
| estrelas | inteiro | contagem | GET /repos/{o}/{r} → stargazers_count | valor na data da coleta | nunca |
| linguagem | texto | não se aplica | GET /repos/{o}/{r} → language | valor copiado | ver dataset_final.csv |
| contribuidores | inteiro | contagem | GET /repos/{o}/{r}/contributors (cabeçalho Link) | número da última página com per_page=1 | ver dataset_final.csv |
| idade_dias | inteiro | dias | GET /repos/{o}/{r} → created_at | fim da janela − created_at | nunca |
| criado_em | data-hora ISO 8601 UTC | não se aplica | GET /repos/{o}/{r} → created_at | valor copiado | nunca |
| coletado_em | data-hora ISO 8601 UTC | não se aplica | pipeline | momento da coleta do repositório | nunca |

## `resultados/funil_selecao.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| etapa | categórico | não se aplica | pipeline | populacao_busca, candidatos_examinados, sem_actions, com_actions, releases_insuficientes, runs_insuficientes, elegiveis, erros_persistentes, erros_pendentes, amostra_final | nunca |
| quantidade | inteiro | contagem | pipeline (progresso/) | candidatos_examinados = sem_actions + com_actions + erros_persistentes + erros_pendentes; com_actions = releases_insuficientes + runs_insuficientes + elegiveis | nunca |

## `resultados/releases_janela.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | pipeline | owner/nome | nunca |
| tag | texto | não se aplica | GET /repos/{o}/{r}/releases → tag_name | valor copiado | nunca |
| nome | texto | não se aplica | GET releases → name | valor copiado | release sem nome |
| published_at | data-hora ISO 8601 UTC | não se aplica | GET releases → published_at | somente releases publicadas na janela; drafts excluídos | nunca |
| prerelease | booleano | não se aplica | GET releases → prerelease | valor copiado | nunca |
| tag_anterior | texto | não se aplica | derivado | release publicada imediatamente anterior na sequência sem pré-releases (pode estar fora da janela) | pré-release ou primeira da história |
| published_at_anterior | data-hora ISO 8601 UTC | não se aplica | derivado | published_at da tag_anterior | pré-release ou primeira da história |
| primeira_da_historia | booleano | não se aplica | derivado | true se não existe release anterior no histórico | pré-release ou coleta da Sprint 1 (histórico incompleto) |
| comparacao_disponivel | booleano | não se aplica | GET compare | true se o compare com a tag_anterior retornou commits | pré-release |
| n_commits | inteiro | contagem | GET compare → commits | quantidade de commits incluídos na release | pré-release ou sem comparação |
| tag_anterior_com_pre | texto | não se aplica | derivado | release anterior na sequência que inclui pré-releases (variante da RQ 07) | primeira da história |
| url_release | texto (URL) | não se aplica | derivado | https://github.com/{repo}/releases/tag/{tag} | nunca |
| url_compare | texto (URL) | não se aplica | derivado | https://github.com/{repo}/compare/{tag_anterior}...{tag} | pré-release ou primeira da história |

## `resultados/commits_releases.csv.gz`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | pipeline | owner/nome | nunca |
| tag | texto | não se aplica | GET compare (head) | release que inclui o commit | nunca |
| sha | texto | não se aplica | GET compare → commits[].sha | valor copiado | nunca |
| author_date | data-hora ISO 8601 UTC | não se aplica | GET compare → commits[].commit.author.date | valor copiado (data em que a mudança foi escrita) | nunca |
| mensagem_primeira_linha | texto | não se aplica | GET compare → commits[].commit.message | primeira linha da mensagem | mensagem vazia |

## `resultados/runs.csv.gz`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | pipeline | owner/nome | nunca |
| workflow_id | inteiro | não se aplica | GET actions/runs → workflow_id | valor copiado | nunca |
| workflow_nome | texto | não se aplica | GET actions/runs → name | valor copiado | sem nome |
| run_id | inteiro | não se aplica | GET actions/runs → id | valor copiado | nunca |
| conclusion | categórico | não se aplica | GET actions/runs → conclusion | apenas success, failure, timed_out, startup_failure (demais descartadas na coleta) | nunca |
| created_at | data-hora ISO 8601 UTC | não se aplica | GET actions/runs → created_at | critério da janela | nunca |
| run_started_at | data-hora ISO 8601 UTC | não se aplica | GET actions/runs → run_started_at | início do episódio de falha (RQ 04) | nunca |
| updated_at | data-hora ISO 8601 UTC | não se aplica | GET actions/runs → updated_at | fim do episódio de falha (RQ 04) | nunca |

## `validacao/amostra_ouro_repositorios.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | resultados/amostra_final.csv | amostra_final ordenada por nome; sample(n=60, random_state=42) | nunca |

## `validacao/amostra_ouro_releases.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | amostra_ouro_repositorios.csv | repositório sorteado | nunca |
| tag | texto | não se aplica | releases_janela.csv | até 5 releases por repositório (sem pré-release, com comparação), sample(random_state=42) | nunca |
| tag_anterior | texto | não se aplica | releases_janela.csv | valor copiado | nunca |
| published_at | data-hora ISO 8601 UTC | não se aplica | releases_janela.csv | valor copiado | nunca |
| url_release | texto (URL) | não se aplica | releases_janela.csv | valor copiado | nunca |
| url_compare | texto (URL) | não se aplica | releases_janela.csv | valor copiado | nunca |

## `validacao/rotulos/rotulos_<avaliador>_repositorios.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | amostra_ouro_repositorios.csv | valor copiado | nunca |
| url_repositorio | texto (URL) | não se aplica | derivado | https://github.com/{repo} | nunca |
| tipo_projeto | categórico | não se aplica | rotulagem manual independente | biblioteca_framework \| aplicacao_servico \| ferramenta_cli \| outro | antes da rotulagem |
| entregas_reais | categórico | não se aplica | rotulagem manual independente | sim \| nao \| incerto | antes da rotulagem |
| observacoes | texto | não se aplica | avaliador | texto livre | sem observação |

## `validacao/rotulos/rotulos_<avaliador>_releases.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | amostra_ouro_releases.csv | valor copiado | nunca |
| tag | texto | não se aplica | amostra_ouro_releases.csv | valor copiado | nunca |
| tag_anterior | texto | não se aplica | amostra_ouro_releases.csv | valor copiado | nunca |
| url_release | texto (URL) | não se aplica | amostra_ouro_releases.csv | valor copiado | nunca |
| url_compare | texto (URL) | não se aplica | amostra_ouro_releases.csv | valor copiado | nunca |
| corretiva | categórico | não se aplica | rotulagem manual independente | sim \| nao (a release tem como objetivo principal corrigir um defeito recente) | antes da rotulagem |
| observacoes | texto | não se aplica | avaliador | texto livre | sem observação |

## `validacao/concordancia.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| dimensao | categórico | não se aplica | validacao.concordancia | tipo_projeto \| entregas_reais \| corretiva | nunca |
| nivel | categórico | não se aplica | validacao.concordancia | repositorios \| releases | nunca |
| n_itens | inteiro | contagem | rótulos | itens rotulados pelos três | nunca |
| n_avaliadores | inteiro | contagem | rótulos | 3 | nunca |
| n_categorias_usadas | inteiro | contagem | rótulos | categorias distintas efetivamente usadas | nunca |
| kappa_fleiss | decimal | adimensional (−1 a 1) | statsmodels aggregate_raters + fleiss_kappa | κ = (P̄ − P̄e) ÷ (1 − P̄e) | todos usaram uma única categoria (indefinido) |
| interpretacao | categórico | não se aplica | Landis & Koch (1977) | <0 pobre; ≤0,20 leve; ≤0,40 razoável; ≤0,60 moderada; ≤0,80 substancial; >0,80 quase perfeita | nunca |
| concordancia_unanime | decimal | proporção (0–1) | rótulos | itens em que os três concordam ÷ n_itens | nunca |
| concordancia_pares | decimal | proporção (0–1) | rótulos | pares de avaliadores concordantes ÷ total de pares | nunca |

## `validacao/divergencias.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| nivel | categórico | não se aplica | validacao.concordancia | repositorios \| releases | nunca |
| repositorio | texto | não se aplica | rótulos | item divergente | nunca |
| tag | texto | não se aplica | rótulos | release divergente | nível repositorios |
| dimensao | categórico | não se aplica | validacao.concordancia | dimensão em que houve divergência | nunca |
| rotulo_bruna | categórico | não se aplica | rotulos_bruna_*.csv | rótulo atribuído pelo avaliador | nunca |
| rotulo_ana | categórico | não se aplica | rotulos_ana_*.csv | rótulo atribuído pelo avaliador | nunca |
| rotulo_walter | categórico | não se aplica | rotulos_walter_*.csv | rótulo atribuído pelo avaliador | nunca |
| padrao | categórico | não se aplica | derivado | 2-1 (maioria) ou 1-1-1 (empate) | nunca |

## `validacao/decisoes_reuniao.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| nivel | categórico | não se aplica | reunião de consenso | repositorios \| releases | nunca |
| repositorio | texto | não se aplica | reunião de consenso | item decidido | nunca |
| tag | texto | não se aplica | reunião de consenso | release decidida | nível repositorios |
| dimensao | categórico | não se aplica | reunião de consenso | dimensão decidida | nunca |
| rotulo | categórico | não se aplica | reunião de consenso | rótulo final (vocabulário da dimensão) | nunca |
| justificativa | texto | não se aplica | reunião de consenso | motivo da decisão (obrigatório) | nunca |
| data | data ISO 8601 | não se aplica | reunião de consenso | data da reunião | nunca |
| presentes | texto | não se aplica | reunião de consenso | avaliadores presentes, separados por ; | nunca |

## `validacao/consenso_repositorios.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | rótulos | item da amostra-ouro | nunca |
| tipo_projeto | categórico | não se aplica | validacao.consenso | maioria dos três; empates decididos em reunião | nunca |
| origem_tipo_projeto | categórico | não se aplica | validacao.consenso | unanime \| maioria \| reuniao | nunca |
| entregas_reais | categórico | não se aplica | validacao.consenso | maioria dos três; empates decididos em reunião | nunca |
| origem_entregas_reais | categórico | não se aplica | validacao.consenso | unanime \| maioria \| reuniao | nunca |

## `validacao/consenso_releases.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | rótulos | item da amostra-ouro | nunca |
| tag | texto | não se aplica | rótulos | release sorteada | nunca |
| corretiva | categórico | não se aplica | validacao.consenso | maioria dos três (sim \| nao) | nunca |
| origem_corretiva | categórico | não se aplica | validacao.consenso | unanime \| maioria \| reuniao | nunca |

## `validacao/heuristica_versoes.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| versao | texto | não se aplica | validacao.avaliar_heuristica (precision_recall_fscore_support) | chave de heuristica.VERSOES | nunca |
| descricao_regra | texto | não se aplica | validacao.avaliar_heuristica (precision_recall_fscore_support) | heuristica.DESCRICOES | nunca |
| n_releases | inteiro | contagem | validacao.avaliar_heuristica (precision_recall_fscore_support) | releases do consenso avaliadas | nunca |
| tp | inteiro | contagem | validacao.avaliar_heuristica (precision_recall_fscore_support) | heurística = corretiva e consenso = sim | nunca |
| fp | inteiro | contagem | validacao.avaliar_heuristica (precision_recall_fscore_support) | heurística = corretiva e consenso = nao | nunca |
| fn | inteiro | contagem | validacao.avaliar_heuristica (precision_recall_fscore_support) | heurística = não corretiva e consenso = sim | nunca |
| tn | inteiro | contagem | validacao.avaliar_heuristica (precision_recall_fscore_support) | heurística = não corretiva e consenso = nao | nunca |
| precisao | decimal | proporção (0–1) | validacao.avaliar_heuristica (precision_recall_fscore_support) | tp ÷ (tp + fp) | nunca |
| recall | decimal | proporção (0–1) | validacao.avaliar_heuristica (precision_recall_fscore_support) | tp ÷ (tp + fn) | nunca |
| f1 | decimal | proporção (0–1) | validacao.avaliar_heuristica (precision_recall_fscore_support) | 2·P·R ÷ (P + R) | nunca |
| atinge_limiar | booleano | não se aplica | validacao.avaliar_heuristica (precision_recall_fscore_support) | f1 ≥ 0,70 | nunca |
| data | data ISO 8601 | não se aplica | validacao.avaliar_heuristica (precision_recall_fscore_support) | data da avaliação | nunca |
| commit | texto | não se aplica | validacao.avaliar_heuristica (precision_recall_fscore_support) | git rev-parse --short HEAD no momento da avaliação | git indisponível |

## `validacao/erros_heuristica_<versao>.csv`

| Campo | Tipo | Unidade | Origem | Fórmula / regra | Quando vazio |
|---|---|---|---|---|---|
| repositorio | texto | não se aplica | validacao.avaliar_heuristica | release classificada incorretamente | nunca |
| tag | texto | não se aplica | validacao.avaliar_heuristica | valor copiado | nunca |
| tag_anterior | texto | não se aplica | validacao.avaliar_heuristica | valor copiado | nunca |
| consenso | inteiro (0/1) | não se aplica | validacao.avaliar_heuristica | 1 = corretiva no consenso | nunca |
| heuristica | inteiro (0/1) | não se aplica | validacao.avaliar_heuristica | 1 = corretiva pela heurística | nunca |
| tipo_erro | categórico | não se aplica | validacao.avaliar_heuristica | falso_positivo \| falso_negativo | nunca |
| url_compare | texto (URL) | não se aplica | validacao.avaliar_heuristica | valor copiado | nunca |
| mensagens | texto | não se aplica | validacao.avaliar_heuristica | primeiras linhas dos commits, separadas por \| | nunca |
