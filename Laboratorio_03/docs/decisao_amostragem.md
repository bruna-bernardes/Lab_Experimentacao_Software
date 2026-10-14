# Decisão da estratégia de amostragem — Lab03S02

**Responsável:** Bruna · **Issue:** Lab03_Sprint02 - Estratégia de amostragem de candidatos

## Problema observado na Sprint 1
A seleção percorria as faixas de estrelas em ordem (1.001–2.000, 2.001–5.000, …) e, dentro de cada faixa, o fatiamento recursivo da busca começava pelos intervalos mais baixos. Como a coleta parava ao atingir 100 elegíveis, os 100 repositórios da S1 ficaram entre 1.001 e 1.891 estrelas, e 75% deles têm até 1.025 estrelas. A busca também usava `sort=updated`, uma ordem que muda de um dia para o outro.

Consequências: os quartis de popularidade da RQ 06 ficariam praticamente sem variação, e a amostra representaria só a faixa mais baixa de "repositórios populares" (ameaça à validade externa).

## Decisão
1. **População:** todos os repositórios devolvidos por `GET /search/repositories?q=stars:1001..1000000 archived:false fork:false`, fatiados por faixas e subdivididos enquanto a busca indicar mais de 1.000 resultados. Usamos `sort=stars` para estabilidade.
2. **Ordem de exame:** o pool é deduplicado, ordenado por nome e **embaralhado com semente fixa** (`semente_amostragem = 42` no `config.json`, `random.Random(42)`). Isso equivale a uma amostra aleatória simples sobre a população de candidatos. Não usamos estratificação para não impor proporções arbitrárias entre faixas.
3. **Congelamento:** o pool embaralhado é salvo em `dados/janela_*/pool_candidatos.json`, com data da busca, semente e tamanho, na primeira execução. As execuções seguintes reutilizam o arquivo, então a ordem não muda mesmo se o cache HTTP for apagado.
4. **Critério de parada:** os candidatos são examinados nessa ordem até haver `quantidade` elegíveis (320, margem sobre o mínimo de 300). A amostra final é o conjunto de todos os elegíveis encontrados.
5. **Sprint 1 como piloto:** os 100 repositórios da S1 não são forçados na amostra. Os que forem sorteados novamente são reaproveitados pelo cache, sem custo de API.

## Outras mudanças na seleção
- Os contribuidores são contados pelo cabeçalho `Link` (`per_page=1&anon=true`), uma única chamada por repositório, e apenas para os elegíveis.
- `idade_dias` é calculado em relação ao **fim da janela**, e não à data da execução.

## Custo esperado
Montar o pool exige algumas centenas de chamadas à Search API, que tem limite próprio de 30 requisições por minuto. O `GitHubAPI` espera automaticamente quando a cota acaba. A etapa é feita uma única vez e fica em cache.

## Registro para a Metodologia
- Data da busca: `<pendente: pool_candidatos.json → data_busca>`
- Tamanho da população: `<pendente: funil_selecao.csv → populacao_busca>`
