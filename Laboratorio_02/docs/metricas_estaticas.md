# Coleta de Métricas Estáticas

A coleta de métricas estáticas do Lab02 será realizada sobre o código final produzido em cada trial.

## Métricas

### Complexidade ciclomática média

Coletada com **Radon** sobre as funções e métodos do código Python.

Para cada trial será registrada a média da complexidade ciclomática das funções e métodos encontrados.

### LOC

Coletada com **Radon** e utilizada como métrica de controle para a RQ3.

O valor registrado corresponde ao total de linhas físicas dos arquivos de implementação analisados.

### Duplicação

Coletada com **jscpd**.

A configuração utilizada está versionada no arquivo `.jscpd.json`, mantendo os mesmos parâmetros para todos os trials:

- mínimo de 5 linhas por bloco duplicado;
- mínimo de 50 tokens;
- modo `mild`.

Os arquivos de testes não devem ser incluídos na medição do código produzido pelo participante.

## Teste do script

Para testar sem gravar dados no CSV oficial:

```bash
python scripts/coletar_metricas.py --arquivo katas/teste_runner/solucao.py --somente-exibir
```

## Execução oficial

Exemplo para um trial:

```bash
python scripts/coletar_metricas.py --arquivo katas/kata_01/solucao.py --participante Bruna --kata kata_01 --tratamento COM_IA
```

O resultado será acrescentado em:

```text
dados/metricas_estaticas.csv
```

O CSV conterá:

- participante;
- kata;
- tratamento;
- caminho analisado;
- LOC;
- quantidade de funções/métodos analisados;
- complexidade ciclomática média;
- percentual de duplicação;
- quantidade de linhas duplicadas.
