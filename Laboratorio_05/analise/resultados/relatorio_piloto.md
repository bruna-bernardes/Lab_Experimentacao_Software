# Piloto da Sprint 1 — análise

**Responsável:** Walter Louback (análise e impacto)
**Amostra:** 8 páginas, mediana de 3 repetições cada (24 respostas HTTP)
**Quando:** 18/11/2026 19:10–19:11 (horário de Brasília)
**Plano:** `planejamento/proposta_s01.md`

Este relatório descreve o piloto. Ele testa o instrumento e mostra a ordem de grandeza das medidas. A conclusão do estudo fica para a amostra da Sprint 2.

## 1. Unidade de análise

Cada página entra uma vez. As três repetições estimam o ruído da medição; a unidade dos testes é a mediana delas. Tratar as 24 respostas como observações independentes inflaria a amostra.

A rubrica de segurança foi a mesma nas três repetições de cada página.

## 2. Descritiva

Mediana das três repetições. Tempos em milissegundos. Bytes são os transferidos com `Accept-Encoding: gzip`.

| Página | Grupo | Tempo total | Mín.–máx. das repetições | TTFB | Bytes | Pontuação | Conjunto mínimo | Cache |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Página inicial | portal | 167 | 152–193 | 121 | 21.965 | 6/8 | 1 | HIT |
| Catálogo de serviços | portal | 163 | 145–194 | 143 | 15.175 | 6/8 | 1 | HIT |
| Categorias | portal | 162 | 156–181 | 128 | 26.390 | 6/8 | 1 | HIT |
| Órgãos do governo | portal | 162 | 151–179 | 128 | 15.102 | 6/8 | 1 | HIT |
| INSS | órgão | 226 | 211–229 | 142 | 46.564 | 6/8 | 1 | HIT |
| Ministério da Saúde | órgão | 218 | 199–242 | 164 | 32.480 | 6/8 | 1 | HIT |
| Trabalho e Emprego | órgão | 202 | 164–227 | 126 | 30.146 | 6/8 | 1 | HIT |
| MEC | órgão | 231 | 227–252 | 148 | 38.207 | 6/8 | 1 | HIT |

Tempo total, nas medianas das páginas: mediana 185 ms, mínimo 162 ms, máximo 231 ms.

Cache observado: HIT. O tempo descreve a resposta que este cliente anônimo recebeu, inclusive quando ela veio de cache.

Cabeçalho `Server` em 6 das 8 páginas: Zope/(2.13.28, python 2.7.16, linux2) ZServer/1.1. Ausente em Ministério da Saúde, MEC. O banner identifica a pilha anunciada pela resposta; não é uma auditoria do ambiente.

Figuras: `figuras/tempo_total.png`, `figuras/bytes_transferidos.png`, `figuras/pontuacao_seguranca.png`.

## 3. Testes do piloto

α = 0,05, testes bicaudais, sem correção para múltiplas comparações. O piloto não decide o estudo. As duas perguntas primárias declaradas no plano são o tempo total e a proporção do conjunto mínimo. Peso, TTFB e pontuação são secundários.

H₀ do tempo, do peso, do TTFB e da pontuação: a distribuição do grupo órgão é igual à do grupo portal. O delta de Cliff é P(órgão > portal) − P(órgão < portal). Limiares de magnitude de Romano et al. (2006): 0,147, 0,33 e 0,474.

| Métrica | Mediana portal | Mediana órgão | Diferença | Teste | U | p | Decisão | Delta de Cliff |
|---|---:|---:|---:|---|---:|---:|---|---|
| Tempo total (ms) | 162,6 | 221,9 | 59,3 ms | exato | 16,0 | 0,0286 | rejeita H₀ | 1,00 (grande) |
| TTFB (ms) | 128,1 | 144,9 | 16,9 ms | exato | 12,0 | 0,3429 | não rejeita H₀ | 0,50 (grande) |
| Bytes transferidos | 18.570,0 | 35.343,5 | 16.773,5 bytes | exato | 16,0 | 0,0286 | rejeita H₀ | 1,00 (grande) |
| Pontuação (0–8) | 6,0 | 6,0 | 0,0 pontos | exato | 8,0 | 1,0000 | não rejeita H₀ | 0,00 (desprezível) |

Nesta lista, rejeitam H₀: tempo total, bytes transferidos. Não rejeitam H₀: TTFB, pontuação. Isso descreve as oito páginas. A amostra da Sprint 2 é que repete a pergunta.

H₀ da proporção, primária: p = 0,80. A barra de 80% é convenção deste estudo, no mesmo espírito da meta de 5% do Laboratório 04. Não é um SLO publicado pelo governo.

| Teste | Estimativa | Estatística | p | Decisão |
|---|---:|---:|---:|---|
| Z para uma proporção | 8/8 = 100,0% | Z = 1,41 | 0,1573 | não rejeita H₀ |
| Binomial exato | 8/8 = 100,0% | — | 0,3709 | não rejeita H₀ |

Intervalo exato de 95% para p: [63,1%; 100,0%].

n·p₀ = 6,4 e n·(1−p₀) = 1,6. Como n·(1−p₀) fica abaixo de 5, a aproximação normal do teste Z não vale para esta amostra. A leitura do piloto segue o teste binomial exato, o mesmo critério praticado no Laboratório 04.

Com 8 páginas, o intervalo ainda é largo. Uma taxa de 100% nesta amostra convive com valores bem mais baixos no intervalo. Para ter cerca de 80% de poder para distinguir p = 0,50 de p₀ = 0,80, no teste bicaudal com α = 0,05, a conta normal pede cerca de 17 páginas. A Sprint 2 precisa passar desse tamanho. Oito páginas servem para ensaiar o instrumento.

## 4. Impacto, em cenário

A fonte pública usada aqui é a Agência Gov, via MGI, em 13/04/2026: mais de 80 milhões de pessoas acessaram o GOV.BR em março de 2026, e o trimestre janeiro–março teve 1,7 bilhão de acessos. Acesso em 18/11/2026: <https://agenciagov.ebc.com.br/noticias/202604/gov-br-ultrapassa-80-milhoes-de-acessos-unicos-mensais>.

No piloto, a mediana do tempo total do HTML foi 185 ms por página, em conexão nova, nesta rede. Para uma pessoa, isso é uma fração de segundo de espera pelo HTML, antes de CSS, JavaScript e imagens.

Cenário, não medição: se cada uma das 80 milhões de pessoas — o piso publicado para março — tivesse esperado esse tempo mediano uma única vez, a espera somada seria de 4.103 horas. O mesmo cenário, aplicado à mediana de 28.268 bytes transferidos, soma 2.106,1 GiB. O número coletivo fica grande porque multiplica uma espera pequena por muita gente. Ele não mede o tempo que os cidadãos perderam.

O trimestre de 1,7 bilhão de acessos não entra nessa conta. Aqueles acessos misturam páginas, aplicativos, sessões autenticadas e cache em outras redes. Multiplicá-los por este HTML inflaria o impacto sem uma definição de acesso que a gente tenha medido.

O que o piloto sustenta, se a amostra maior repetir o padrão: a política de cabeçalhos destas páginas é propriedade da plataforma, não de cada órgão, e o peso do HTML varia entre as páginas. Uma espera de algumas centenas de milissegundos no HTML anônimo não descreve o Meu INSS, o Meu SUS Digital nem o uso no celular.

## 5. O que esta análise não fecha

- Não há alocação de tratamento. Um p-valor pequeno indicaria diferença entre os grupos medidos, não a causa dela.
- Oito páginas e uma rede, num único horário, não representam os mais de 13 mil serviços nem os aplicativos.
- O tempo de HTML em conexão fria não é o tempo da página pronta no navegador.
- O conjunto mínimo e a pontuação observam cabeçalhos publicados. Não medem vulnerabilidade.
- A Lei de Goodhart cabe no desenho: se só o conjunto mínimo virasse meta, um CSP restrito a `frame-ancestors` passaria e a ausência de `script-src` sumiria da conta. Por isso a pontuação guarda os itens separados.
