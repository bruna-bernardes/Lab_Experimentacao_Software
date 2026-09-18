from decimal import Decimal, InvalidOperation
import math


def calcular_total_pedido(
    itens,
    cupom=None,
    retirada=False,
    cliente_vip=False
):
    if not isinstance(itens, list) or not itens:
        raise ValueError("itens deve ser uma lista não vazia")

    subtotal = Decimal("0")
    for item in itens:
        if not isinstance(item, dict) or "preco" not in item or "quantidade" not in item:
            raise ValueError("cada item deve conter preco e quantidade")

        preco = item["preco"]
        quantidade = item["quantidade"]
        if (
            isinstance(preco, bool)
            or not isinstance(preco, (int, float))
            or not math.isfinite(preco)
            or preco <= 0
        ):
            raise ValueError("preco deve ser maior que zero")
        if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade <= 0:
            raise ValueError("quantidade deve ser um inteiro maior que zero")

        try:
            subtotal += Decimal(str(preco)) * quantidade
        except (InvalidOperation, ValueError):
            raise ValueError("preco inválido") from None

    if cupom not in (None, "DESC10", "DESC20"):
        raise ValueError("cupom inválido")

    total = subtotal
    if cupom == "DESC10" and subtotal >= Decimal("100"):
        total *= Decimal("0.90")
    elif cupom == "DESC20" and subtotal >= Decimal("200"):
        total *= Decimal("0.80")

    if cliente_vip:
        total *= Decimal("0.95")

    if not retirada and subtotal < Decimal("150"):
        total += Decimal("15")

    return float(total.quantize(Decimal("0.01")))
