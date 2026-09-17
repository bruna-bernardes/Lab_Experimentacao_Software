def calcular_total_pedido(
    itens,
    cupom=None,
    retirada=False,
    cliente_vip=False
):
    if not itens:
        raise ValueError("A lista de itens não pode estar vazia.")

    subtotalOriginal = 0

    for item in itens:
        preco = item["preco"]
        quantidade = item["quantidade"]

        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")

        if not isinstance(quantidade, int) or quantidade <= 0:
            raise ValueError(
                "A quantidade deve ser um número inteiro maior que zero."
            )

        subtotalOriginal += preco * quantidade

    valorComDescontos = subtotalOriginal

    if cupom == "DESC10" and subtotalOriginal >= 100:
        valorComDescontos = valorComDescontos * 0.9
    elif cupom == "DESC20" and subtotalOriginal >= 200:
        valorComDescontos = valorComDescontos * 0.8

    if cliente_vip:
        valorComDescontos = valorComDescontos * 0.95

    valorFrete = 0

    if not retirada and subtotalOriginal < 150:
        valorFrete = 15

    total = valorComDescontos + valorFrete

    return round(total, 2)