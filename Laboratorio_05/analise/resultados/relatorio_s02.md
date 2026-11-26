# Amostra confirmatória da Sprint 2 — análise

**Responsável:** Walter Louback (análise e impacto)
**Amostra:** 18 páginas (9 de entrada do portal e 9 de órgão), mediana das duas janelas
**Noite:** 25/11/2026 23:21–23:22 (horário de Brasília)
**Dia:** 26/11/2026 14:38–14:38 (horário de Brasília)
**Respostas HTTP:** 108, três repetições em cada janela
**Plano:** `planejamento/proposta_s01.md`

Este relatório repete as hipóteses da Sprint 1 na amostra maior. Não troca a rubrica e não trata o p-valor como causa.

## 1. Unidade de análise

Cada página entra uma vez. Dentro de uma janela, as três repetições viram uma mediana. Entre as janelas, o número do teste é a mediana dessas duas medianas. As duas janelas não viram duas observações, e as seis respostas não viram seis.

A rubrica de segurança foi a mesma nas repetições e nas duas janelas de cada página.

## 2. Descritiva

O tempo da tabela é o que entra no teste, em milissegundos. Noite e dia são as medianas de cada janela, antes de serem combinadas. Bytes são os transferidos com `Accept-Encoding: gzip`.

| Página | Grupo | Tempo no teste | Noite | Dia | TTFB | Bytes | Pontuação | Conjunto mínimo | Cache |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Página inicial | portal | 133 | 140 | 126 | 97 | 22.076 | 6/8 | 1 | HIT |
| Catálogo de serviços | portal | 97 | 96 | 98 | 94 | 15.166 | 6/8 | 1 | HIT |
| Categorias | portal | 119 | 120 | 119 | 97 | 26.390 | 6/8 | 1 | HIT |
| Órgãos do governo | portal | 104 | 108 | 101 | 96 | 15.102 | 6/8 | 1 | HIT |
| Aplicativos | portal | 106 | 96 | 116 | 95 | 13.887 | 6/8 | 1 | HIT |
| Acessibilidade | portal | 95 | 96 | 93 | 94 | 13.072 | 6/8 | 1 | HIT |
| Por dentro do gov.br | portal | 117 | 117 | 117 | 94 | 11.047 | 6/8 | 1 | HIT |
| Sobre o gov.br | portal | 116 | 119 | 113 | 93 | 16.350 | 6/8 | 1 | HIT |
| Termos de uso | portal | 118 | 114 | 122 | 96 | 26.991 | 6/8 | 1 | HIT |
| INSS | órgão | 182 | 192 | 171 | 104 | 46.626 | 6/8 | 1 | HIT |
| Ministério da Saúde | órgão | 123 | 120 | 127 | 100 | 32.212 | 6/8 | 1 | HIT |
| Trabalho e Emprego | órgão | 120 | 120 | 120 | 97 | 30.157 | 6/8 | 1 | HIT |
| MEC | órgão | 180 | 211 | 150 | 114 | 37.812 | 6/8 | 1 | HIT |
| Ministério da Fazenda | órgão | 144 | 167 | 121 | 109 | 25.728 | 6/8 | 1 | HIT |
| Ministério da Agricultura | órgão | 123 | 124 | 122 | 99 | 40.412 | 6/8 | 1 | HIT |
| Ministério das Cidades | órgão | 137 | 154 | 120 | 97 | 29.571 | 6/8 | 1 | HIT |
| Ministério da Cultura | órgão | 147 | 166 | 128 | 97 | 31.868 | 6/8 | 1 | HIT |
| Ministério da Defesa | órgão | 133 | 120 | 146 | 98 | 29.388 | 6/8 | 1 | HIT |

Tempo usado no teste: mediana 121 ms, mínimo 95 ms, máximo 182 ms.

Cache observado: HIT. O tempo descreve a resposta que este cliente anônimo recebeu, inclusive quando ela veio de cache.

Figuras: `figuras/s02_tempo_total.png`, `figuras/s02_bytes_transferidos.png`, `figuras/s02_pontuacao_seguranca.png`.

## 3. Testes

α = 0,05, testes bicaudais, sem correção para múltiplas comparações. As duas perguntas primárias continuam sendo o tempo total e a proporção do conjunto mínimo. Peso, TTFB e pontuação são secundários. O grupo portal e o grupo órgão têm 9 páginas cada.

H₀ do tempo, do peso, do TTFB e da pontuação: a distribuição do grupo órgão é igual à do grupo portal. O delta de Cliff é P(órgão > portal) − P(órgão < portal). Limiares de magnitude de Romano et al. (2006): 0,147, 0,33 e 0,474.

| Métrica | Mediana portal | Mediana órgão | Diferença | Teste | U | p | Decisão | Delta de Cliff |
|---|---:|---:|---:|---|---:|---:|---|---|
| Tempo total (ms) | 116,3 | 136,9 | 20,6 ms | exato | 77,0 | 0,0005 | rejeita H₀ | 0,90 (grande) |
| TTFB (ms) | 95,1 | 99,5 | 4,4 ms | exato | 81,0 | 4,11e-05 | rejeita H₀ | 1,00 (grande) |
| Bytes transferidos | 15.166,5 | 31.868,0 | 16.701,5 bytes | exato | 79,0 | 0,0002 | rejeita H₀ | 0,95 (grande) |
| Pontuação (0–8) | 6,0 | 6,0 | 0,0 pontos | exato | 40,5 | 1,0000 | não rejeita H₀ | 0,00 (desprezível) |

Nesta lista, rejeitam H₀: tempo total, bytes transferidos, TTFB. Não rejeitam H₀: pontuação.

No tempo total, a direção da diferença é a mesma do piloto. No peso, a direção da diferença é a mesma do piloto. O piloto tinha 4 páginas em cada grupo; esta amostra amplia as duas listas e não repete o mesmo conjunto.

H₀ da proporção, primária: p = 0,80. A barra de 80% continua sendo convenção deste estudo. Não é um SLO do governo.

| Teste | Estimativa | Estatística | p | Decisão |
|---|---:|---:|---:|---|
| Z para uma proporção | 18/18 = 100,0% | Z = 2,12 | 0,0339 | rejeita H₀ |
| Binomial exato | 18/18 = 100,0% | — | 0,0343 | rejeita H₀ |

Intervalo exato de 95% para p: [81,5%; 100,0%].

n·p₀ = 14,4 e n·(1−p₀) = 3,6. Como um dos dois fica abaixo de 5, a aproximação normal do teste Z não vale para esta amostra. A leitura segue o teste binomial exato, o mesmo critério do Laboratório 04 e do piloto.

A amostra tem 18 páginas, acima das cerca de 17 que o piloto pediu para distinguir p = 0,50 de p₀ = 0,80. O que apareceu não foi uma queda para 50%: 18 de 18 páginas passaram no conjunto mínimo. O teste exato rejeita p = 0,80 porque a taxa observada ficou acima da barra, e o intervalo começa em 81,5%, logo acima de 80%. Isso não mostra falha de cabeçalho. Mostra que, se a taxa fosse exatamente 80%, observar 100,0% nesta lista seria pouco comum. Também não prova que o portal inteiro está nessa taxa.

## 4. As duas janelas

A comparação entre noite e dia não é uma terceira hipótese primária. Ela só pergunta se o horário mudou o tempo da mesma página. O teste é o Wilcoxon pareado, bicaudal, sobre as medianas de cada janela. n = 18 páginas, não 36.

| Comparação | Mediana da diferença (dia − noite) | Teste | Estatística | p | Decisão |
|---|---:|---|---:|---:|---|
| Tempo total (ms) | -2,7 ms | Wilcoxon pareado | 51,0 | 0,1415 | não rejeita H₀ |

Duas janelas não são uma amostra de horários do dia. Um resultado estável aqui diz que estas duas corridas se pareceram. Não diz que o portal é o mesmo de manhã, de tarde e de madrugada.

## 5. Impacto, em cenário

A fonte pública continua sendo a Agência Gov, via MGI, em 13/04/2026: mais de 80 milhões de pessoas acessaram o GOV.BR em março de 2026. Acesso em 18/11/2026: <https://agenciagov.ebc.com.br/noticias/202604/gov-br-ultrapassa-80-milhoes-de-acessos-unicos-mensais>. O 1,7 bilhão de acessos do trimestre não entra na multiplicação.

Nesta amostra, a mediana do tempo usado no teste foi 121 ms por página, em conexão nova, nesta rede. Para uma pessoa, isso é uma fração de segundo de espera pelo HTML, antes de CSS, JavaScript e imagens.

Cenário, não medição: se cada uma das 80 milhões de pessoas tivesse esperado esse tempo mediano uma única vez, a espera somada seria de 2.697 horas. O mesmo cenário, aplicado à mediana de 26.690 bytes transferidos, soma 1.988,6 GiB. O número coletivo fica grande porque multiplica uma espera pequena por muita gente. Ele não mede o tempo que os cidadãos perderam.

O que esta amostra sustenta, e o que ela não sustenta, está nas ameaças da Sprint 2. Uma diferença entre os grupos medidos não explica a causa. O HTML anônimo destas páginas não descreve o Meu INSS, o Meu SUS Digital nem o uso no celular.

## 6. O que a conta não fecha

- Não há alocação de tratamento. Rejeitar H₀ descreve os grupos medidos.
- A lista não é amostra aleatória dos mais de 13 mil serviços.
- O tempo de HTML em conexão fria não é o tempo da página pronta no navegador.
- Cabeçalho publicado não é vulnerabilidade, e cabeçalho ausente também não.
- Se só o conjunto mínimo virasse meta, um CSP restrito a `frame-ancestors` passaria e a ausência de `script-src` sairia da conta. A pontuação guarda os itens separados por isso.
