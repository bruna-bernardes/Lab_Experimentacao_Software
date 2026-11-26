# Análise e impacto — Sprint 1

**Responsável:** Walter Louback
**Papel:** análise e impacto

Esta pasta consome o CSV produzido em `instrumentacao/dados/piloto_s01.csv`. Não coleta página nenhuma. A coleta versionada é o piloto de registro; rodar a análise de novo, com o mesmo CSV, reproduz o relatório e as figuras.

## Como executar

Na pasta `Laboratorio_05/analise`, com as dependências de `requirements.txt`:

```bash
python3 test_analise.py
python3 analisar_piloto.py
```

O script recusa o CSV se `instrumentacao/validar_piloto.py` apontar problema. O texto numérico fica em `resultados/relatorio_piloto.md`.

## Escolhas herdadas do plano

O plano metodológico está em `planejamento/proposta_s01.md`. Aqui ele vira conta.

- Unidade: a página. As três repetições viram uma mediana. Segurança usa o pior valor das repetições, se elas discordarem.
- Tempo, peso, TTFB e pontuação: Mann-Whitney bicaudal, método exato, α = 0,05. A pontuação é ordinal; o teste compara as distribuições e o relatório não trata a média como “grau de segurança”.
- Tamanho de efeito: delta de Cliff, com a leitura de magnitude de Romano et al. (2006).
- Proporção do conjunto mínimo: H₀ p = 0,80, teste Z e teste binomial exato, os dois do Laboratório 04. A conclusão usa o teste exato quando n·p₀ ou n·(1−p₀) fica abaixo de 5.
- O piloto não corrige múltiplas comparações e não fecha o estudo. A conta de tamanho de amostra indica quantas páginas a Sprint 2 precisa para um efeito grande na proporção.
- Impacto: tempo mediano por pessoa, mais um cenário que multiplica esse tempo pelo piso de 80 milhões de acessos únicos em março de 2026. O 1,7 bilhão de acessos do trimestre fica de fora da multiplicação.

## Sprint 2

O script `analisar_s02.py` lê as duas janelas já validadas em `instrumentacao/dados/coleta_s02_noite.csv` e `coleta_s02_dia.csv`. Não coleta página. Cada página entra uma vez: a mediana das três repetições de cada janela e, em seguida, a mediana dessas duas medianas. As seis respostas não viram seis observações.

```bash
python3 test_analise.py
python3 analisar_s02.py
```

O texto fica em `resultados/relatorio_s02.md`. O relatório do piloto não é reescrito. O comando recusa a conta se uma janela não existir ou se a validação apontar problema.

## O que esta pasta não faz

Não redefine a pergunta, não altera a rubrica e não inclui requisição ao portal. Isso está no planejamento e na instrumentação.
