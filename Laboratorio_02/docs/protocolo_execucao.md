# Protocolo de Execução dos Trials

Este protocolo deve ser seguido em todos os trials do Lab02 para manter as condições do experimento consistentes.

## Antes do trial

1. Confirmar participante, kata, tratamento e ordem no arquivo `dados/plano_trials.csv`.
2. Fechar materiais ou soluções de outros katas.
3. Garantir que o participante não tenha acesso às soluções dos demais integrantes.
4. Abrir somente o enunciado, os testes e o arquivo inicial do kata correspondente.
5. Confirmar que o ambiente virtual está ativo.
6. Confirmar que os testes automatizados executam corretamente.
7. Se o tratamento for `COM_IA`, utilizar somente o assistente definido pelo grupo.
8. Se o tratamento for `SEM_IA`, não utilizar qualquer assistente de IA generativa.

## Início

Executar o script de coleta informando participante, kata e tratamento.

Exemplo:

```bash
python scripts/executar_trial.py --participante Ana --kata kata_01 --tratamento SEM_IA --caminho-kata katas/kata_01
```

O cronômetro começa somente após a confirmação do participante.

## Durante o trial

- limite máximo: 35 minutos;
- não pausar o cronômetro;
- não trocar de tratamento;
- não consultar soluções produzidas anteriormente;
- não receber ajuda de outros integrantes;
- salvar o código normalmente para permitir a execução automática dos testes.

## Encerramento

O trial termina quando:

1. todos os testes de aceitação passam; ou
2. o limite de 35 minutos é atingido.

Se o time-box for atingido sem sucesso, o tempo deve permanecer registrado como 35 minutos e o trial deve ser marcado como censurado.

Após o encerramento:

- não alterar mais a solução;
- registrar o estado final dos testes;
- executar as métricas estáticas;
- preservar o código final produzido naquele trial.

## Dados mínimos esperados

- participante;
- kata;
- tratamento;
- início;
- fim;
- tempo;
- censura;
- quantidade total de testes;
- testes passando;
- testes falhando;
- taxa de sucesso;
- complexidade ciclomática média;
- LOC;
- duplicação percentual.

## Regras de rastreabilidade

Cada trial oficial da Sprint 2 deverá possuir uma Issue individual no GitHub Projects contendo:

- kata;
- tratamento;
- participante responsável;
- Assignee;
- referência ao commit correspondente.
