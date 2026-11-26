# Lab 05 — Sprint 2 · A amostra confirmatória

**Responsável:** Ana Luiza (planejamento e método)
**Data:** 26 de novembro de 2026
**Plano que esta nota não reabre:** `proposta_s01.md`
**Corrida:** `instrumentacao/protocolo_coleta_s02.md`
**Números:** `analise/resultados/relatorio_s02.md`

A Sprint 1 deixou as hipóteses, a rubrica e o α escritas antes de ver o piloto. Esta nota diz por que a amostra da Sprint 2 é esta, e o que ela não é. Não recalcula p-valor.

## 1. Por que 18 páginas

O piloto tinha 8 páginas, 4 de cada grupo. A análise dele estimou que cerca de 17 páginas dariam poder próximo de 80% para distinguir uma taxa de 50% de uma taxa de 80% no conjunto mínimo, no teste bicaudal com α = 0,05. Esse piso vale para a proporção, que usa todas as páginas juntas. Não é uma conta separada para o Mann-Whitney.

A lista fechou em 18: 9 páginas do portal e 9 páginas iniciais de órgão. Dezoito passa o piso e deixa os grupos do mesmo tamanho. A sondagem achou mais homes de órgão com resposta 200. Elas não entraram. Um lado órgão bem maior mudaria o desenho da comparação sem aumentar, na mesma proporção, o lado portal. O portal público em `/pt-br` não rendeu 9 páginas de navegação além das que já estão na lista.

A conta de 17 páginas era para um efeito grande, de 80% para 50%. Não era o tamanho necessário para “provar 100%”, nem para detectar uma diferença pequena de tempo.

## 2. A unidade continua sendo a página

Cada página foi medida três vezes em cada janela. São 108 respostas HTTP. Esse número não é o n dos testes.

Dentro da janela, as três repetições estimam o ruído e viram uma mediana. Entre a noite de 25/11, às 23:21, e a tarde de 26/11, às 14:38, o valor da página é a mediana dessas duas medianas. A página entra uma vez. Tratar as duas janelas como duas observações independentes dobraria o n para 36 e fingiria que a mesma URL, na mesma rede, são duas páginas.

A comparação entre os horários existe, mas é outra pergunta: se o tempo da mesma página mudou. Ela usa os 18 pares. Não vira uma terceira hipótese primária e não entra na tabela de portal contra órgão.

## 3. O que permanece da Sprint 1

Não houve correção de instrumento que obrigasse a mudar a rubrica. Permanecem:

- duas hipóteses primárias, as duas bicaudais, α = 0,05;
- tempo total: as distribuições de portal e órgão são iguais, contra a alternativa de que diferem; Mann-Whitney exato; delta de Cliff;
- conjunto mínimo: p = 0,80 contra p diferente de 0,80; teste Z e teste binomial exato; a leitura fica no teste exato quando n·p₀ ou n·(1−p₀) fica abaixo de 5;
- secundárias, com a mesma H₀ de igualdade de distribuições: TTFB, bytes e pontuação.

A barra de 80% continua sendo convenção deste estudo, no espírito da meta de 5% do Laboratório 04. Não é um SLO do governo. O teste é bicaudal porque uma taxa acima de 80% e uma taxa abaixo de 80% são, as duas, afastamentos da barra. Rejeitar H₀ não diz, sozinho, se o afastamento é para cima ou para baixo: isso se lê na estimativa.

Não há correção para múltiplas comparações. As duas primárias foram declaradas antes. TTFB, bytes e pontuação continuam secundários. Um p-valor pequeno numa secundária não troca essa ordem.

## 4. O que a segunda janela responde

Responde se, nestas 18 páginas e nesta rede, o tempo mediano da tarde ficou diferente do tempo mediano da noite. São duas ocasiões, separadas por cerca de 15 horas. Não são uma amostra de horários do dia, nem de dias da semana, nem de redes.

Não responde se o cidadão no celular, em outra cidade, vê o mesmo tempo. Não transforma o estudo em longitudinal no sentido de acompanhar o portal ao longo do tempo. São duas fotografias.

## 5. O que esta nota não faz

Não escolhe o teste depois de ver a tabela. Não troca H₀ porque a proporção deu 18/18. Não trata o cenário de 80 milhões de pessoas como medição: esse uso do número público está no relatório de análise, com o limite de que ele multiplica uma espera, não observa a espera dos cidadãos.
