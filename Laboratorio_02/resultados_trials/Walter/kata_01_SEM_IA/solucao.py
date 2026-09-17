def calcular_tarifa_entrega(
    peso_kg,
    distancia_km,
    expressa=False,
    cliente_premium=False
):
    if peso_kg <= 0:
        raise ValueError("O peso deve ser maior que zero.")

    if distancia_km <= 0:
        raise ValueError("A distância deve ser maior que zero.")

    valor = 10

    if peso_kg <= 2:
        valor += 0
    elif peso_kg <= 5:
        valor += 4
    elif peso_kg <= 10:
        valor += 8
    else:
        valor += 15

    if distancia_km <= 20:
        valor += 0
    elif distancia_km <= 100:
        valor += 5
    else:
        valor += 12

    if expressa:
        valor = valor * 1.5

    if cliente_premium:
        valor = valor * 0.9

    return round(valor, 2)