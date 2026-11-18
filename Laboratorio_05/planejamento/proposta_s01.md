# Lab 05 — Sprint 1 · Proposta

**Disciplina:** Laboratório de Experimentação de Software
**Professor:** Danilo Maia
**Grupo:** Ana Luiza, Bruna Bernardes e Walter Louback
**Responsável por este documento:** Ana Luiza (planejamento e método)
**Data:** 18 de novembro de 2026

A Sprint 1 registra a proposta, a primeira versão das categorias do estudo e o plano. A coleta piloto e a análise numérica estão nas pastas de Bruna e de Walter. Os números do piloto não entram aqui, para o plano não ser ajustado depois de ver o resultado.

## 1. O software

O objeto é o **portal GOV.BR** servido em `www.gov.br`: as páginas HTML públicas que um visitante anônimo recebe. O portal é a porta de entrada dos serviços digitais federais, mantida com apoio do Serpro e do Ministério da Gestão e da Inovação em Serviços Públicos.

Ficam de fora o código-fonte, os commits e as issues. Também ficam de fora, nesta sprint, os aplicativos e os sistemas de consulta autenticada (Meu INSS, Meu SUS Digital, Enem, Carteira de Trabalho Digital). Eles aparecem só como contexto de impacto. O que se mede é o portal em `www.gov.br`.

## 2. Os três critérios

Acesso às fontes em 18/11/2026.

| Critério | Evidência | Fonte |
|---|---|---|
| Real | O portal existe, tem endereço oficial e é o canal publicado de serviços digitais do governo federal. | <https://www.gov.br/pt-br> |
| Em operação | Em 13/04/2026 a Agência Gov descreveu a plataforma em uso, com recorde no mês anterior. Em 18/11/2026 as páginas públicas do piloto respondem a um GET anônimo. Na sondagem de viabilidade do mesmo dia, a resposta trouxe `Server: Zope/(2.13.28, python 2.7.16, linux2) ZServer/1.1` atrás de Varnish. É a pilha anunciada em produção nessa data, não um protótipo do grupo. | [Agência Gov, 13/04/2026](https://agenciagov.ebc.com.br/noticias/202604/gov-br-ultrapassa-80-milhoes-de-acessos-unicos-mensais); sondagem registrada em `instrumentacao/protocolo_coleta.md` |
| Alto impacto | Mais de 80 milhões de pessoas acessaram o GOV.BR em março de 2026. A mesma matéria relata mais de 175 milhões de usuários, 1,7 bilhão de acessos entre janeiro e março de 2026 e mais de 13 mil serviços digitais, sendo 4.600 federais e 8.700 de estados e municípios. | [Agência Gov, via MGI, 13/04/2026](https://agenciagov.ebc.com.br/noticias/202604/gov-br-ultrapassa-80-milhoes-de-acessos-unicos-mensais) |

O banner `Server` mostra Zope 2.13 e Python 2.7.16. Python 2.7 não recebe mais correção upstream. Isso entra como atributo observado da resposta. O estudo não sonda vulnerabilidade nem descreve como atacar essa pilha.

## 3. Pergunta e caminho

**Pergunta de pesquisa.** Nas páginas públicas do portal GOV.BR, quanto tempo e quantos bytes um cliente anônimo precisa para receber o HTML, qual fração dessas páginas envia um conjunto mínimo de cabeçalhos de segurança, e as páginas iniciais dos órgãos ligados aos serviços de maior uso diferem das páginas de entrada do portal?

Caminhos da seção 2 do enunciado, combinados:

- **Medir o serviço de fora**, como um usuário anônimo, no máximo uma requisição por segundo.
- **Avaliar a qualidade do produto** em duas características da ISO/IEC 25010: eficiência de desempenho (comportamento no tempo e volume transferido) e segurança, esta última só pelos cabeçalhos HTTP publicados.

A pergunta pede o que o cidadão recebe em produção. Por isso o grupo mede o portal no ar, em vez de instalar um software local e variar a versão.

## 4. GQM

Objetivo, no formato de Basili:

> Analisar **as páginas HTML públicas do portal GOV.BR** com o propósito de **caracterizar** com respeito ao **tempo de resposta, ao volume transferido e aos cabeçalhos de segurança HTTP** do ponto de vista do **cidadão anônimo** no contexto de **uma coleta pontual, com no máximo uma requisição por segundo, a partir da rede do grupo**.

| Pergunta | Métrica | Papel |
|---|---|---|
| Quanto tempo leva receber o HTML? | `tempo_total_ms` e `ttfb_ms` | Tempo total é primário. TTFB é secundário. |
| Quanto se transfere? | `bytes_transferidos` | Secundário. `bytes_html` fica no dicionário como tamanho decodificado. |
| As páginas enviam o conjunto mínimo? | `atende_conjunto_minimo` e a proporção p | Primário. |
| A proteção publicada vai além do mínimo? | `pontuacao_seguranca` (0 a 8) e os oito indicadores | Secundário. A escala é ordinal. |
| Entrada do portal e página de órgão diferem? | As métricas acima, comparadas entre os dois grupos | Primário para o tempo; secundário para peso, TTFB e pontuação. |

Conjunto mínimo, definido antes da coleta piloto: `Strict-Transport-Security` com `max-age` positivo, `X-Content-Type-Options: nosniff`, proteção contra clickjacking (`X-Frame-Options` ou `frame-ancestors`), `Referrer-Policy` e algum `Content-Security-Policy`.

A pontuação soma o conjunto mínimo com três itens que o mínimo não exige: `includeSubDomains` no HSTS, `default-src` ou `script-src` no CSP, e `Permissions-Policy`. Um CSP que só contém `frame-ancestors` conta no mínimo e não conta como restrição de script.

## 5. Entidades, atributos e escalas

A entidade é o produto: a resposta HTML de uma página pública. Não é o processo de desenvolvimento nem o repositório.

| Métrica | Atributo | Direta ou derivada | Escala | O que a escala autoriza |
|---|---|---|---|---|
| `tempo_total_ms`, `ttfb_ms`, `tempo_tls_ms` | Externo, eficiência de desempenho | Direta | Razão | Mediana, média, desvio, comparação de distribuições |
| `bytes_transferidos`, `bytes_html` | Externo, volume | Direta | Razão | O mesmo |
| Cada indicador de cabeçalho | Externo, segurança publicada | Direta | Nominal | Frequência e moda |
| `atende_conjunto_minimo` | Externo, derivado dos cinco itens | Derivada | Nominal binária | Proporção e teste para proporção |
| `pontuacao_seguranca` | Externo, soma dos oito itens | Derivada | Ordinal | Mediana e comparação de distribuições. A diferença de um ponto não é “o dobro de segurança”, e a média não é tratada como intensidade |
| `cache`, `servidor` | Contexto da resposta | Direta | Nominal | Frequência. Entram como leitura do construto, não como métrica de qualidade |

Os tempos incluem o aperto de mão TLS de uma conexão nova. `tempo_tls_ms` fica registrado para a Sprint 2 separar, se fizer falta, o custo da conexão do custo até o primeiro byte.

## 6. Hipóteses e desenho

O desenho é observacional. O grupo não escolhe versão, configuração nem carga. Os dois grupos já existem na arquitetura do portal:

- **Portal:** página inicial, catálogo de serviços, categorias e índice de órgãos.
- **Órgão:** páginas iniciais, no próprio `www.gov.br`, do INSS, do Ministério da Saúde, do Ministério do Trabalho e Emprego e do MEC. A matéria do MGI cita Meu INSS, Meu SUS Digital, Carteira de Trabalho Digital, Enem e Fies entre os serviços de maior uso. Estas quatro URLs são a página institucional desses órgãos no portal, não o sistema transacional.

Três repetições por página, em rodadas, estimam o ruído. A unidade dos testes é a página: a mediana das três repetições. Há 4 páginas em cada grupo no piloto (n = 8).

Hipóteses, bicaudais, α = 0,05, escritas antes da análise do piloto:

1. **Tempo total (primária).** H₀: a distribuição de `tempo_total_ms` é a mesma nos dois grupos. H₁: as distribuições diferem. Teste de Mann-Whitney, método exato. Tamanho de efeito: delta de Cliff.
2. **Conjunto mínimo (primária).** H₀: p = 0,80. H₁: p ≠ 0,80. A barra de 80% é convenção deste estudo, análoga à meta de 5% do Laboratório 04. Não é um SLO do governo. Teste Z para uma proporção e teste binomial exato. A conclusão segue o teste exato quando n·p₀ ou n·(1−p₀) é menor que 5.
3. **Secundárias.** A mesma H₀ de igualdade de distribuições para `ttfb_ms`, `bytes_transferidos` e `pontuacao_seguranca`.

O piloto não corrige múltiplas comparações. Também não encerra o estudo: a sondagem de viabilidade já tinha visitado as URLs, e n = 8 tem pouco poder. Os p-valores da Sprint 1 mostram o procedimento. A amostra confirmatória é a da Sprint 2.

## 7. Sete categorias — primeira versão

| Categoria | Classificação | Justificativa |
|---|---|---|
| Natureza | Aplicada | O resultado conversa com quem opera o portal e com quem usa. |
| Objetivos | Descritiva | O estudo caracteriza tempo, peso e cabeçalhos. Há hipótese de diferença entre grupos, e o desenho continua descritivo: sem tratamento aplicado, uma diferença não explica a causa. |
| Abordagem | Quantitativa | As métricas são numéricas e os testes também. |
| Procedimentos | Estudo de caso observacional | Um software, no contexto real de produção, medido por fora. Não há alocação de tratamento, então o rótulo de experimento controlado não cabe. |
| Tempo | Transversal | Uma janela só. Repetir em outros horários, na Sprint 2, é o que tornaria parte do estudo longitudinal. |
| Controle | Baixo, em campo | O servidor, o cache e a rota estão fora do controle do grupo. O que se controla é o cliente: lista de URLs, cadência, cabeçalhos do pedido e a regra de não guardar corpo nem cookie. |
| Nível de evidência | Observacional | Serve para descrever o que este cliente recebeu. Fica abaixo de um quase-experimento e de um experimento. Não sustenta “trocar o órgão reduz o tempo”. |

Esta tabela será revisada na Sprint 3, quando a amostra e a análise estiverem fechadas.

## 8. Armadilhas de medição

A Lei de Goodhart e a lei de Campbell cabem na rubrica. Se o conjunto mínimo virasse a única meta, um CSP restrito a `frame-ancestors` seria tratado como sucesso e a falta de `script-src` ou de `Permissions-Policy` sairia da conta. A pontuação guarda os itens separados para essa folga não desaparecer.

A falácia de McNamara também cabe. Tempo de HTML e cabeçalhos não medem se o serviço resolve o problema do cidadão, se o texto é compreensível ou se a fila do INSS anda. O estudo declara esse recorte na validade de construto e de novo no impacto.

## 9. Ameaças à validade — primeira versão

**Conclusão estatística.** n = 8 e três repetições correlacionadas. Mitigação: agregar antes do teste, declarar duas primárias, tratar o piloto como ensaio e calcular, na análise, quantas páginas a Sprint 2 precisa para um efeito grande na proporção. Ruído de rede permanece; as repetições existem para torná-lo visível.

**Interna.** Não há alocação aleatória. Conteúdo, tamanho, cache e horário podem seguir juntos. Mitigação honesta: não usar o p-valor como causa. A comparação entre grupos, na mesma rede e na mesma janela, é mais estável que o valor absoluto do tempo. A ordem em rodadas reduz a chance de uma página ficar inteira num momento atípico.

**Construto.** O tempo até o fim do HTML não é o tempo da página pronta. A conexão é fria, então o TLS entra no TTFB. O pedido aceita gzip e não anuncia Brotli; o byte transferido pode ser maior que o de um navegador atual. Cabeçalho presente não é segurança realizada, e cabeçalho ausente não é vulnerabilidade demonstrada. O cache, quando a resposta vem dele, mede a borda da rede, não a origem. Mitigação: registrar TLS, encoding, cache e banner; limitar a conclusão ao que foi medido.

**Externa.** Oito páginas, uma rede e um horário não representam os mais de 13 mil serviços, o uso no celular nem a sessão autenticada. Mitigação: escrever o cenário de impacto com o piso de acessos únicos e dizer, no mesmo parágrafo, o que o número não é. A Sprint 2 amplia páginas e horários; não transforma o estudo em censo.

## 10. Plano de coleta e de análise

**Coleta.** Operação em `instrumentacao/protocolo_coleta.md`. Em resumo: oito URLs, três repetições em rodadas, só GET, no máximo uma requisição por segundo, `robots.txt` consultado antes, sem login, sem corpo de página e sem cookie gravados. O piloto que vale é o CSV versionado, não a sondagem anterior.

**Análise.** Operação em `analise/LEIA-ME.md`. Em resumo: validar o CSV, agregar pela mediana, aplicar os testes da seção 6, reportar o delta de Cliff e o intervalo exato de p, e separar o que é primário. A análise para se a validação falhar.

**Impacto.** Duas peças, as duas com fonte:

- O tempo mediano por pessoa, na unidade em que a espera acontece (milissegundos).
- Um cenário coletivo: esse tempo multiplicado por 80 milhões, o piso de acessos únicos de março de 2026 publicado pela Agência Gov. Uma pessoa, uma espera, uma vez.

O 1,7 bilhão de acessos do trimestre documenta o impacto do software. Não entra como multiplicador da latência medida. Aqueles acessos não são o HTML destas oito páginas.

## 11. O que vem dos laboratórios anteriores

| Laboratório | O que entra neste estudo |
|---|---|
| Lab 01 | Coleta automatizada, registro estruturado e separação entre coletar e analisar. |
| Lab 02 | Protocolo, grupos, repetição e a decisão explícita do que conta como uma observação. |
| Lab 03 | Dicionário de dados, validação antes da conta e pipeline reprodutível. As métricas DORA não são reaproveitadas: o objeto aqui é o portal em operação, não um fluxo de entrega. |
| Lab 04 | Teste Z e teste binomial exato lado a lado, a regra n·p₀ ≥ 5 e n·(1−p₀) ≥ 5, α = 0,05 e a leitura de amostra pequena. O painel da entrega final pode reaproveitar a ideia do dashboard; não faz parte desta sprint. |

## 12. Esta sprint e a seguinte

A Sprint 1 entrega a proposta, as categorias, o plano, o piloto validado e a análise exploratória desse piloto.

A Sprint 2 amplia a lista de páginas para além do tamanho calculado no piloto, repete a coleta em outro horário, congela o novo CSV e refaz os testes primários nessa amostra. A rubrica e as hipóteses acima permanecem, salvo correção de instrumento encontrada na validação.
