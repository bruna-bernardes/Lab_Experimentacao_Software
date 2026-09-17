def calcular_total_pedido(
    itens,
    cupom=None,
    retirada=False,
    cliente_vip=False
):
    if not itens:
        raise ValueError("A lista de itens não pode estar vazia.")
    
    subtotal = 0
    
    for item in itens:
        preco = item ["preco"]
        quantidade = item["quantidade"]
        
        if preco <= 0:
            raise ValueError("O preço do item deve ser maior que zero.")
        
        if not isinstance(quantidade, int) or quantidade <= 0:
            raise ValueError("A quantidade do item deve ser um número inteiro positivo.")
        
        subtotal += preco * quantidade
        
    valor = subtotal
    
    if cupom == "DESC10" and subtotal >= 100:
        valor = valor * 0.90
    
    elif cupom == "DESC20" and subtotal >= 200:
        valor = valor * 0.80
        
    if cliente_vip:
        valor = valor * 0.95
        
    if not retirada and subtotal < 150:
        valor += 15.00
        
    return round(valor, 2)