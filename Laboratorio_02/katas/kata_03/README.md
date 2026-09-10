# Kata 03 — Processamento de Pedidos

Implemente a função:

```python
calcular_total_pedido(
    itens,
    cupom=None,
    retirada=False,
    cliente_vip=False
)
```

`itens` será uma lista de dicionários no formato:

```python
[
    {"preco": 30.00, "quantidade": 2},
    {"preco": 20.00, "quantidade": 1}
]
```

## Regras

O subtotal é calculado por `preco × quantidade` para todos os itens.

### Cupons

- `DESC10`: 10% de desconto quando o subtotal for pelo menos R$ 100,00;
- `DESC20`: 20% de desconto quando o subtotal for pelo menos R$ 200,00.

Se o subtotal mínimo não for atingido, o cupom não concede desconto.

### Cliente VIP

Se `cliente_vip=True`, aplicar mais **5% de desconto** após o desconto do cupom.

Os descontos de cupom e VIP são cumulativos.

### Frete

O frete custa **R$ 15,00** quando:

- o pedido não é para retirada; e
- o subtotal original é inferior a R$ 150,00.

Pedidos com subtotal igual ou superior a R$ 150,00 possuem frete grátis.

Se `retirada=True`, não há cobrança de frete.

A regra do frete utiliza o subtotal **antes dos descontos**.

### Validação

- a lista de itens não pode estar vazia;
- preço deve ser maior que zero;
- quantidade deve ser um número inteiro maior que zero.

Dados inválidos devem gerar `ValueError`.

O resultado deve ser arredondado para **2 casas decimais**.
