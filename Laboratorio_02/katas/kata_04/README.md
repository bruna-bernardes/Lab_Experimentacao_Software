# Kata 04 — Classificação de Chamados por SLA

Implemente a função:

```python
avaliar_sla(
    prioridade,
    horas_aberto,
    cliente_vip=False,
    indisponibilidade_total=False
)
```

A função deve retornar um dicionário:

```python
{
    "prazo_horas": 24.0,
    "status": "DENTRO"
}
```

## Prazo padrão por prioridade

- `baixa`: 72 horas;
- `media`: 48 horas;
- `alta`: 24 horas;
- `critica`: 8 horas.

A prioridade deve ser tratada sem diferença entre maiúsculas e minúsculas.

## Cliente VIP

Se `cliente_vip=True`, reduzir o prazo em **25%**.

## Indisponibilidade total

Se `indisponibilidade_total=True`, o prazo máximo passa a ser **4 horas**.

Se outro cálculo já resultar em prazo menor que 4 horas, deve ser mantido o menor prazo.

## Status

Após determinar o prazo final:

- `ESTOURADO`: quando `horas_aberto` for maior que o prazo;
- `ATENCAO`: quando `horas_aberto` for maior ou igual a 75% do prazo, sem ultrapassá-lo;
- `DENTRO`: quando estiver abaixo de 75% do prazo.

## Validação

- prioridade deve ser uma das quatro opções aceitas;
- `horas_aberto` não pode ser negativo.

Dados inválidos devem gerar `ValueError`.

O prazo retornado deve ser arredondado para **2 casas decimais**.
