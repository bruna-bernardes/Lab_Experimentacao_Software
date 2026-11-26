# Lab 05 — Sprint 2 · Ameaças à validade

**Responsável:** Ana Luiza (planejamento e método)
**Data:** 26 de novembro de 2026
**Amostra:** 18 páginas, duas janelas, 108 respostas HTTP; o n dos testes é 18
**Números citados daqui:** `analise/resultados/relatorio_s02.md`

A primeira versão destas ameaças está na proposta da Sprint 1. O que muda é o que a amostra confirmatória já permite dizer, e o que continua aberto. As 7 categorias não são revisadas aqui.

## 1. Conclusão estatística

O piloto tinha n = 8 e um intervalo largo para a proporção. Agora são 18 páginas, acima do piso de cerca de 17 que aquela conta pedia para um efeito grande na proporção. O n não é 108. Usar cada resposta como observação independente trataria repetições da mesma página como páginas novas.

n·p₀ = 14,4 e n·(1−p₀) = 3,6. O segundo produto continua abaixo de 5, então a aproximação normal do teste Z não é a leitura. O teste binomial exato é. Ele rejeita p = 0,80, com intervalo de 81,5% a 100%. As 18 páginas passaram no conjunto mínimo. A rejeição é para cima da barra, não para baixo: não é evidência de cabeçalho faltando. A distância até 80% é pequena. O intervalo ainda admite taxas logo acima da barra. Dizer “o portal está em 100%” passa do que o intervalo segura.

No tempo, no TTFB e nos bytes, o Mann-Whitney exato rejeita a igualdade dos grupos, com delta de Cliff grande. Na pontuação, os dois grupos ficam em 6/8 e o teste não rejeita. Tempo e proporção eram as primárias. TTFB e bytes eram secundários. Não houve correção para as várias comparações. A chance de algum p-valor pequeno, entre cinco testes, é maior do que α sozinho sugere. A ordem declarada na Sprint 1 continua valendo: a secundária não vira o resultado principal só porque também rejeitou.

Entre as janelas, o Wilcoxon pareado sobre o tempo não rejeita. A mediana da diferença foi cerca de −3 ms. Isso reduz a suspeita de que uma das duas corridas tenha sido um horário absurdo. Não aumenta o n e não cria precisão que a lista de 18 páginas não tem.

O que mitiga: agregar antes de testar, manter o teste exato na proporção, e separar primária de secundária. O que não se mitiga: a lista não foi sorteada, e cinco testes sem correção continuam no relatório.

## 2. Interna

Não há alocação. Portal e órgão já existiam. Conteúdo, tamanho do HTML e o caminho até a borda podem andar juntos. As páginas de órgão vieram mais pesadas no piloto e de novo aqui. Um p-valor pequeno no tempo não diz que “ser órgão” causa os cerca de 20 ms a mais. Pode ser o peso, o template, o cache daquela URL.

As duas janelas saíram da mesma rede e da mesma máquina, uma às 23:21 e outra às 14:38. O Wilcoxon não achou diferença prática de tempo. Isso afasta um pouco a hipótese de que o resultado seja só um minuto atípico. Não afasta o fato de que as duas corridas compartilham cliente, rota e cache. Quase tudo veio HIT. O que se comparou foi a borda que este cliente encontrou, nas duas vezes.

O que mitiga: a mesma lista, a mesma cadência, a ordem em rodadas, e a checagem pareada entre horários. O que não se mitiga: não dá para separar o efeito do grupo do efeito do conteúdo da página.

## 3. Construto

O tempo até o fim do HTML não é o tempo da página pronta. A conexão é fria, então o TLS entra no TTFB. O pedido anuncia gzip e não anuncia Brotli. O byte transferido pode ser maior que o de um navegador atual. Cabeçalho presente não é segurança realizada. A pontuação ficou em 6/8 em todas as páginas: o conjunto mínimo entrou, e os três itens além dele não separaram os grupos. Se a meta única fosse o mínimo, essa folga de dois pontos sumiria da conversa. Foi por isso que a rubrica guardou os itens separados, e a ameaça da Lei de Goodhart continua de pé.

O cache HIT mede a resposta que este visitante anônimo recebeu. Não mede a origem sem cache. O estudo não pediu para furar cache, de propósito.

O que mitiga: registrar TLS, encoding, cache e a rubrica item a item, e limitar a frase ao que foi medido. O que não se mitiga: o construto “qualidade do serviço para o cidadão” é mais largo do que HTML e cabeçalho.

## 4. Externa

Dezoito páginas, uma rede, dois horários. Isso não representa os mais de 13 mil serviços, o uso no celular, nem a sessão autenticada. Meu INSS, Meu SUS Digital, Enem e Carteira de Trabalho Digital continuam fora. A página inicial do INSS no portal não é o Meu INSS.

O cenário de impacto multiplica a mediana de 121 ms por 80 milhões de pessoas e chega a cerca de 2,7 mil horas. É uma conta de cenário, com a fonte da Agência Gov já citada na Sprint 1. Não é a espera que aqueles acessos tiveram. Os 1,7 bilhão de acessos do trimestre continuam de fora da multiplicação, pelo mesmo motivo do piloto: não são o HTML destas 18 páginas.

O que mitiga: dizer o piso de páginas, os dois horários e, no mesmo lugar, o que o número coletivo não é. O que não se mitiga: duas fotografias não viram o comportamento do portal no país.

## 5. O que a Sprint 3 ainda tem de revisar

As 7 categorias foram escritas com o estudo ainda transversal e com o piloto. A segunda janela não basta para reclassificar o tempo do estudo. Essa revisão fica para quando a conclusão estiver fechada, não neste arquivo.
