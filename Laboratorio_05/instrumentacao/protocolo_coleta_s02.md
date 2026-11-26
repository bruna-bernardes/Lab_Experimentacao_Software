# Protocolo da coleta confirmatória

**Responsável:** Bruna Bernardes (instrumentação e operação)
**Sprint:** Lab 05 S02
**Software medido:** portal GOV.BR em `www.gov.br`

O plano da Sprint 1 está em `planejamento/proposta_s01.md`. A justificativa do tamanho e da unidade da amostra fica em `planejamento/amostra_s02.md`. Este arquivo é a regra da corrida. O coletor continua sendo `medicao.py`. `coleta_s02.py` grava uma janela. `validar_s02.py` confere o CSV antes da análise.

## 1. O que muda em relação ao piloto

O piloto mediu 8 páginas, uma vez, em 18/11/2026. A Sprint 2 mede 18 páginas, duas vezes, em horários diferentes. As colunas são as mesmas. A janela não é uma coluna: está no nome do arquivo.

São 9 páginas do próprio portal, com URL final em `/pt-br`, e 9 páginas iniciais de órgão. O piloto tinha 4 e 4. A conta de poder do piloto pedia cerca de 17 páginas para a proporção. Dezoito passa desse piso e mantém os grupos do mesmo tamanho. Havia mais homes de órgão com resposta 200. Elas ficaram de fora para o lado órgão não ficar maior que o lado portal.

Cada janela repete o mesmo roteiro: três repetições em rodadas, só GET, no máximo uma requisição por segundo. A noite e o dia não são a mesma corrida lançada duas vezes.

## 2. Lista congelada

Arquivo `urls_s02.csv`.

| id | Grupo | Papel |
|---|---|---|
| `portal-inicial` | portal | Página inicial, já no piloto |
| `portal-servicos` | portal | Catálogo de serviços, já no piloto |
| `portal-categorias` | portal | Categorias, já no piloto |
| `portal-orgaos` | portal | Índice de órgãos, já no piloto |
| `portal-apps` | portal | Página de aplicativos do portal |
| `portal-acessibilidade` | portal | Página de acessibilidade do portal |
| `portal-por-dentro` | portal | Por dentro do gov.br |
| `portal-sobre` | portal | Sobre o gov.br |
| `portal-termos` | portal | Termos de uso do portal |
| `orgao-inss` | órgão | Página inicial do INSS, já no piloto |
| `orgao-saude` | órgão | Página inicial do Ministério da Saúde, já no piloto |
| `orgao-trabalho` | órgão | Página inicial de Trabalho e Emprego, já no piloto |
| `orgao-mec` | órgão | Página inicial do MEC, já no piloto |
| `orgao-fazenda` | órgão | Página inicial do Ministério da Fazenda |
| `orgao-agricultura` | órgão | Página inicial do Ministério da Agricultura |
| `orgao-cidades` | órgão | Página inicial do Ministério das Cidades |
| `orgao-cultura` | órgão | Página inicial do Ministério da Cultura |
| `orgao-defesa` | órgão | Página inicial do Ministério da Defesa |

As quatro páginas novas do portal continuam no sítio público do portal. Não são o sistema do órgão. Termos de uso e a página sobre o portal entram porque respondem em `/pt-br` sem login. Não são transação de serviço.

## 3. Sondagem de 25/11/2026

Antes da coleta da noite, um GET por URL candidata, também a no máximo uma por segundo. A sondagem não entra no CSV. Entrou na lista quem respondeu 200 e terminou em `www.gov.br`, sem cair em tela de login.

Ficou de fora:

- 404: aplicativos, canais de atendimento, mapa do site, conteúdos, apps no computador, governo, faq, indicadores, contato, política de privacidade, consulta de CPF em `/pt-br/servicos/...`, e a home tentada de Justiça e Segurança Pública.
- Saiu de `www.gov.br`: participação social foi para `brasilparticipativo.presidencia.gov.br`. O caminho `/pt-br/noticias` já tinha sido descartado no piloto pelo mesmo motivo.
- Login: campanhas e ouvidoria redirecionaram para `acl_users/credentials_cookie_auth/require_login`.
- 403: home tentada de Meio Ambiente.
- Respondeu 200 e mesmo assim não entrou, para os grupos ficarem com 9 páginas cada: Economia, Previdência, Receita Federal, Polícia Federal, Anvisa, Inep, Ibama, Capes, Gestão, MCTI, Minas e Energia, Turismo, Esporte, Desenvolvimento Social e Transportes. Economia e Previdência ainda se sobrepõem, no recorte do estudo, a Fazenda e INSS.

## 4. As duas janelas

| Janela | Arquivo | Quando |
|---|---|---|
| `noite` | `dados/coleta_s02_noite.csv` | 25/11/2026, à noite, na rede do grupo |
| `dia` | `dados/coleta_s02_dia.csv` | 26/11/2026, 14:38, horário de Brasília, na mesma rede |

O comando da manhã é o mesmo roteiro. Não se reaproveita o CSV da noite com outro nome.

Se o CSV da janela já existe, `coleta_s02.py` para e não substitui o arquivo. A coleta que vale é a que foi validada. Rodar de novo mudaria o relógio e a análise deixaria de bater com o CSV.

## 5. O que cada corrida faz

São 18 páginas × 3 repetições, mais o GET do `robots.txt`: 55 requisições por janela. As duas janelas, mais a sondagem, ficam na casa de duas centenas de GETs espaçados. Não há teste de carga.

Valem as mesmas regras do piloto: HTTPS, certificado verificado, `User-Agent` identificável, `Accept-Encoding: gzip`, `Connection: close`, no máximo cinco redirecionamentos, corpo limitado a 5 MB, host final `www.gov.br`, ordem em rodadas. O corpo da página e o cookie não são gravados.

`robots.txt` é lido de novo em cada janela. Se alguma URL da lista estiver em `Disallow` para `User-agent: *`, a coleta daquela janela para antes de medir página.

## 6. Validação

`validar_s02.py` usa o mesmo contrato de `validar_piloto.py` em cada janela: colunas, as 54 combinações de página e repetição, status 200, host final, ordem dos tempos, rubrica fechada, intervalo de pelo menos 0,95 s e `robots.txt` com regra `User-agent`.

A saída de cada janela fica em `dados/validacao_s02_noite.json` e `dados/validacao_s02_dia.json`. O comando termina em zero só quando as duas janelas existem e passam. Com só a noite no disco, ele avisa que o dia ainda não foi coletado.

## 7. Como executar

Na pasta `instrumentacao`:

```bash
python3 test_instrumentacao.py
python3 coleta_s02.py --janela noite
python3 coleta_s02.py --janela dia
python3 validar_s02.py
```

As duas janelas já estão em `dados/coleta_s02_noite.csv` e `dados/coleta_s02_dia.csv`. Não apagar esses arquivos para coletar outra vez. Uma corrida nova mudaria o relógio e deixaria de ser a amostra que a análise usou.
