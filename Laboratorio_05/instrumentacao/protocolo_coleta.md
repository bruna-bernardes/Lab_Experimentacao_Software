# Protocolo da coleta piloto

**Responsável:** Bruna Bernardes (instrumentação e operação)
**Sprint:** Lab 05 S01
**Software medido:** portal GOV.BR em `www.gov.br`

O plano metodológico está em `planejamento/proposta_s01.md`. Este arquivo é a regra operacional. O script `medicao.py` implementa a regra; `validar_piloto.py` confere o CSV antes da análise.

## 1. O que a coleta faz

Mede oito páginas públicas, três vezes cada, como um cliente anônimo. Guarda tempos, tamanhos, cache, o banner `Server` e a rubrica de cabeçalhos. Não guarda o HTML, não guarda `Set-Cookie` e não abre sessão.

## 2. Ambiente

Python 3 da biblioteca padrão. Não há servidor instalado pelo grupo: a medição é de fora. A coleta que originou o CSV versionado rodou em 18/11/2026, em WSL2, na rede do grupo.

## 3. Lista de páginas

Arquivo `urls_piloto.csv`.

| id | Grupo | Papel |
|---|---|---|
| `portal-inicial` | portal | Página inicial |
| `portal-servicos` | portal | Catálogo de serviços |
| `portal-categorias` | portal | Categorias |
| `portal-orgaos` | portal | Índice de órgãos, ainda uma página de navegação do portal |
| `orgao-inss` | órgão | Página inicial do INSS no portal |
| `orgao-saude` | órgão | Página inicial do Ministério da Saúde no portal |
| `orgao-trabalho` | órgão | Página inicial de Trabalho e Emprego no portal |
| `orgao-mec` | órgão | Página inicial do MEC no portal |

A escolha dos quatro órgãos segue a proposta: são as páginas institucionais, dentro de `www.gov.br`, dos órgãos ligados aos serviços que a matéria do MGI cita entre os mais usados. Não são o Meu INSS, o Meu SUS, o Enem nem a Carteira de Trabalho.

## 4. Sondagem de viabilidade

Em 18/11/2026, antes do piloto oficial, um GET anônimo confirmou que as oito URLs respondem e permanecem em `www.gov.br`. Essa sondagem não entra no CSV.

`https://www.gov.br/pt-br/noticias` foi descartada nessa sondagem porque redireciona para `agenciagov.ebc.com.br`, outro sítio. O objeto do estudo é o portal em `www.gov.br`.

O mesmo dia mostrou que um HEAD em `https://www.gov.br/robots.txt` voltou 403 e o GET voltou 200. O coletor usa só GET.

## 5. Regras de cada requisição

- Método GET, HTTPS, verificação de certificado ligada.
- No máximo uma requisição por segundo, inclusive o GET do `robots.txt` e cada salto de redirecionamento. A espera não entra no tempo medido.
- `User-Agent` identificável: `LabExperimentacaoSoftware-PUCMinas/1.0`, com a URL do repositório e a indicação de estudo acadêmico sem dados pessoais.
- `Accept-Encoding: gzip`. Brotli não é anunciado; o dicionário registra essa diferença em relação a um navegador.
- `Connection: close`, para cada repetição incluir o TLS de uma conexão nova.
- No máximo cinco redirecionamentos. Se o host final não for `www.gov.br`, a validação reprova a linha.
- Corpo limitado a 5 MB. Acima disso a página é erro, não uma leitura sem teto.
- Tempo marcado no início da requisição, depois que o limitador autoriza o envio.
- Ordem em rodadas: repetição 1 de todas as páginas, depois a repetição 2, depois a 3. Assim as três medidas de uma página não ficam coladas.

O tempo total soma TLS, espera até os cabeçalhos e leitura do corpo. O TTFB inclui o TLS. `tempo_tls_ms` fica numa coluna própria.

## 6. robots.txt

Antes de qualquer página o coletor baixa `https://www.gov.br/robots.txt`. Se o status não for 200, a coleta para. Se alguma URL da lista casar com uma regra `Disallow` do grupo `User-agent: *`, a coleta para e nenhuma página é medida. O texto obtido fica em `dados/robots_www.gov.br.txt`.

O casamento trata `*` como curinga e `$` como fim de caminho. Há teste disso em `test_instrumentacao.py`, sem rede.

## 7. Rubrica gravada em cada linha

Oito indicadores 0/1:

| Coluna | Conta 1 quando |
|---|---|
| `hsts` | `Strict-Transport-Security` com `max-age` maior que zero |
| `nosniff` | `X-Content-Type-Options` contém `nosniff` |
| `clickjacking` | `X-Frame-Options` é DENY ou SAMEORIGIN, ou o CSP tem `frame-ancestors` |
| `referrer_policy` | `Referrer-Policy` presente |
| `csp` | `Content-Security-Policy` presente |
| `hsts_include_subdomains` | o HSTS contém `includeSubDomains` |
| `csp_alem_de_frame` | o CSP contém `default-src` ou `script-src` |
| `permissions_policy` | `Permissions-Policy` presente |

`pontuacao_seguranca` é a soma dos oito. `atende_conjunto_minimo` é 1 só quando os cinco primeiros são 1. Os valores crus dos cabeçalhos vão nas colunas `valor_*`, para a rubrica poder ser refeita sem novo acesso.

`cache` usa, nesta ordem, `X-Cache-F`, `X-Cache` e `X-Cache-B`, e classifica HIT, MISS, OUTRO ou AUSENTE.

## 8. Validação

`validar_piloto.py` reprova o piloto se qualquer item abaixo falhar:

- colunas iguais ao contrato de `medicao.COLUNAS`;
- as 24 combinações de página e repetição, sem duplicata;
- status 200, erro vazio, host final `www.gov.br`;
- `0 ≤ tempo_tls_ms ≤ ttfb_ms ≤ tempo_total_ms` e tamanhos positivos;
- indicadores em {0, 1}, pontuação igual à soma, conjunto mínimo coerente com os cinco itens;
- intervalo de pelo menos 0,95 s entre os instantes gravados;
- `robots.txt` presente e com regra `User-agent`.

A saída fica em `dados/validacao_piloto.json`. A análise não roda com piloto reprovado.

## 9. Ética operacional

- Não há teste de carga nem de estresse. São 25 GETs no piloto (1 do `robots.txt` e 24 páginas), espaçados.
- Não há login, formulário, dado pessoal nem conta real.
- Não se pede para furar cache (`Cache-Control: no-cache` não é enviado). A resposta em cache é a resposta que esse cliente recebe.
- O `User-Agent` identifica o estudo.
- URL fora de `www.gov.br` não entra na lista.

## 10. Como executar

Na pasta `instrumentacao`:

```bash
python3 test_instrumentacao.py
python3 coleta_piloto.py
python3 validar_piloto.py
```

A coleta leva cerca de um minuto por causa do intervalo. Rodar de novo substitui o CSV. O arquivo versionado é o piloto de registro da Sprint 1; a análise usa esse arquivo.
