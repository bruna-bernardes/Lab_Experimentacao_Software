# Kata 02 — Cobrança de Estacionamento

Implemente a função:

```python
calcular_estacionamento(
    minutos,
    fim_de_semana=False,
    mensalista=False
)
```

A função deve calcular o valor final de uma permanência no estacionamento.

## Regras

### Tempo de permanência

- até 30 minutos: R$ 4,00;
- de 31 até 60 minutos: R$ 7,00;
- acima de 60 minutos: R$ 7,00 + R$ 3,00 para cada bloco adicional de 30 minutos iniciado.

Exemplo: 61 minutos já inicia um novo bloco de 30 minutos.

### Limite diário

O valor calculado pelo tempo possui teto de **R$ 35,00**.

O teto deve ser aplicado antes dos ajustes de fim de semana e mensalista.

### Fim de semana

Se `fim_de_semana=True`, acrescentar **20%**.

### Mensalista

Se `mensalista=True`, aplicar **25% de desconto** após os demais cálculos.

### Validação

`minutos` deve ser maior que zero e não pode ultrapassar 1440 minutos.

Valores inválidos devem gerar `ValueError`.

O resultado deve ser arredondado para **2 casas decimais**.
