def calcular_tarifa_entrega(
    peso_kg,
    distancia_km,
    expressa=False,
    cliente_premium=False
):
    if peso_kg <= 0 or distancia_km <= 0:
        raise ValueError("Peso e distância devem ser maiores que zero.")

    tarifa = 10.0

    if peso_kg > 10:
        tarifa += 15
    elif peso_kg > 5:
        tarifa += 8
    elif peso_kg > 2:
        tarifa += 4

    if distancia_km > 100:
        tarifa += 12
    elif distancia_km > 20:
        tarifa += 5

    if expressa:
        tarifa *= 1.5

    if cliente_premium:
        tarifa *= 0.9

    return round(tarifa, 2)
