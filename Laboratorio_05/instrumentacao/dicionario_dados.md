# Dicionário do piloto

**Responsável:** Bruna Bernardes
**Arquivo:** `dados/piloto_s01.csv`
**Uma linha:** uma repetição de uma página

Os tempos estão em milissegundos, com três casas. Os indicadores são 0 ou 1. A definição operacional de cada indicador está em `protocolo_coleta.md`.

| Coluna | Significado |
|---|---|
| `id_pagina` | Identificador estável na lista de URLs |
| `grupo` | `portal` ou `orgao` |
| `rotulo` | Nome legível da página |
| `url_solicitada` | URL da lista |
| `url_final` | URL depois dos redirecionamentos |
| `repeticao` | 1, 2 ou 3 |
| `coletado_em_utc` | Início da requisição, em UTC, depois da espera do limitador |
| `status_http` | Status da resposta final |
| `redirecionamentos` | Saltos seguidos até a resposta final |
| `tempo_tls_ms` | Tempo até a conexão HTTPS ficar pronta |
| `ttfb_ms` | Tempo até os cabeçalhos da resposta final, com o TLS incluído |
| `tempo_total_ms` | Tempo até o fim da leitura do corpo |
| `bytes_transferidos` | Bytes recebidos no fio, já comprimidos quando o encoding é gzip |
| `bytes_html` | Tamanho do corpo depois de descomprimir |
| `content_encoding` | `gzip` ou `identity` |
| `cache` | HIT, MISS, OUTRO ou AUSENTE |
| `servidor` | Valor do cabeçalho `Server`, cortado em 180 caracteres |
| `hsts` | HSTS com max-age positivo |
| `hsts_include_subdomains` | HSTS com includeSubDomains |
| `nosniff` | X-Content-Type-Options nosniff |
| `clickjacking` | X-Frame-Options ou frame-ancestors |
| `referrer_policy` | Referrer-Policy presente |
| `csp` | Content-Security-Policy presente |
| `csp_alem_de_frame` | CSP com default-src ou script-src |
| `permissions_policy` | Permissions-Policy presente |
| `pontuacao_seguranca` | Soma dos oito indicadores, de 0 a 8 |
| `atende_conjunto_minimo` | 1 quando hsts, nosniff, clickjacking, referrer_policy e csp são 1 |
| `valor_hsts` | Texto do cabeçalho HSTS |
| `valor_csp` | Texto do CSP |
| `valor_x_frame_options` | Texto do X-Frame-Options |
| `valor_referrer_policy` | Texto do Referrer-Policy |
| `valor_x_content_type_options` | Texto do X-Content-Type-Options |
| `valor_permissions_policy` | Texto do Permissions-Policy |
| `erro` | Vazio quando a medição completou; mensagem curta quando falhou |

Arquivos ao lado do CSV:

| Arquivo | Conteúdo |
|---|---|
| `piloto_s01_meta.json` | Início, fim, intervalo, user-agent e a nota de que isto é piloto |
| `robots_www.gov.br.txt` | `robots.txt` baixado na mesma execução |
| `validacao_piloto.json` | Resultado da validação, com a lista de problemas |

Não existem colunas de cookie, de IP do cliente, de corpo HTML nem de dado de cidadão.
