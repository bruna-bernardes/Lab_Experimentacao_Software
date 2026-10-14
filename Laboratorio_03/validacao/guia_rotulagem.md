# Guia de rotulagem da amostra-ouro — Lab03S02

Cada avaliador preenche **apenas os próprios arquivos**:
- `validacao/rotulos/rotulos_<nome>_repositorios.csv`
- `validacao/rotulos/rotulos_<nome>_releases.csv`

## Regras de independência
1. Não converse sobre itens específicos da amostra com os outros avaliadores até que os três arquivos estejam commitados.
2. Não execute nem consulte a heurística automática (`heuristica.py`, `validacao/avaliar_heuristica.py`, `dataset_final.csv` → `cfr_entrega`).
3. Dúvidas vão na coluna `observacoes`. Elas serão discutidas na reunião de consenso.
4. Use **exatamente** os valores abaixo, em minúsculas e sem acento.

## (i) `tipo_projeto` — o que o repositório entrega principalmente
| Valor | Quando usar | Pistas |
|---|---|---|
| `biblioteca_framework` | Código para ser importado por outros programas | Publica pacote (PyPI, npm, crates.io, Maven); o README mostra `import`/`install` como dependência |
| `aplicacao_servico` | Programa usado diretamente: app web, desktop, mobile, servidor, serviço | Instruções de deploy ou instalação do app; imagens Docker; binários com interface gráfica |
| `ferramenta_cli` | Programa usado principalmente pela linha de comando | O README mostra comandos de terminal como uso principal |
| `outro` | Nenhum dos anteriores: listas, documentação, dados, configurações, plugins de editor, temas | — |

Se o repositório tiver duas faces, rotule pela que o **README apresenta primeiro**.

## (ii) `entregas_reais` — as releases representam entregas reais ao usuário?
| Valor | Quando usar |
|---|---|
| `sim` | As releases trazem versões utilizáveis (pacotes publicados, binários, notas de versão com mudanças para o usuário) |
| `nao` | As releases são automáticas ou sem significado de entrega (snapshots diários, marcos internos, releases só de CI ou de dados) |
| `incerto` | Não é possível decidir com as informações disponíveis |

## (iii) `corretiva` — a release tem como objetivo principal corrigir um defeito recente?
Abra `url_release` (notas da release) e `url_compare` (commits incluídos).

| Valor | Quando usar |
|---|---|
| `sim` | A maior parte das mudanças corrige defeitos (bugfix, hotfix, revert de algo quebrado) |
| `nao` | A release traz principalmente funcionalidades, melhorias, atualizações de dependências ou mudanças mistas sem predominância de correções |

Julgue pelo **conteúdo**, não pelo número da versão. Uma versão "patch" que só atualiza dependências é `nao`.

## Abrindo e salvando as planilhas
- **VS Code:** abra o CSV direto; a extensão *Edit CSV* ou *Rainbow CSV* ajuda.
- **Excel/LibreOffice:** importe com separador vírgula. Se o Excel salvar com `;` ou em Windows-1252, o validador aceita.
- Para conferir seus arquivos antes do commit: `python -m validacao.concordancia --somente-validar`. Os arquivos dos outros também precisam existir; as planilhas em branco já existem.
