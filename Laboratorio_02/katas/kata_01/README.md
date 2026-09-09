# Kata 01 — Tarifa de Entrega

Implemente a função:

```python
calcular_tarifa_entrega(
    peso_kg,
    distancia_km,
    expressa=False,
    cliente_premium=False
)
```

A função deve calcular o preço final de uma entrega.

## Regras

A tarifa base é de **R$ 10,00**.

### Acréscimo por peso

- até 2 kg: sem acréscimo;
- acima de 2 kg até 5 kg: + R$ 4,00;
- acima de 5 kg até 10 kg: + R$ 8,00;
- acima de 10 kg: + R$ 15,00.

### Acréscimo por distância

- até 20 km: sem acréscimo;
- acima de 20 km até 100 km: + R$ 5,00;
- acima de 100 km: + R$ 12,00.

### Entrega expressa

Se `expressa=True`, acrescentar **50%** sobre o valor obtido após os acréscimos de peso e distância.

### Cliente premium

Se `cliente_premium=True`, aplicar **10% de desconto** sobre o valor após todos os acréscimos.

### Validação

- `peso_kg` deve ser maior que zero;
- `distancia_km` deve ser maior que zero;
- valores inválidos devem gerar `ValueError`.

O resultado deve ser arredondado para **2 casas decimais**.
