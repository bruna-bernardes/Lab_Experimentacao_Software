def calcular_tarifa_entrega(
    peso_kg,
    distancia_km,
    expressa=False,
    cliente_premium=False
):
    if peso_kg <= 0:
        raise ValueError("O peso da encomenda deve ser positivo.")

    if distancia_km <= 0:
        raise ValueError("A distancia da entrega deve ser positiva.")

    faixasPeso = [
        (2, 0.0),
        (5, 4.0),
        (10, 8.0),
    ]

    valorAcrescimoPeso = 15.0

    for limite, acressimo in faixasPeso:
        if peso_kg <= limite:
            valorAcrescimoPeso = acressimo
            break

    faixasDistancia = [
        (20, 0.0),
        (100, 5.0),
    ]

    valorAcrescimoDistancia = 12.0

    for limite, acressimo in faixasDistancia:
        if distancia_km <= limite:
            valorAcrescimoDistancia = acressimo
            break

    valorBase = 10.0 + valorAcrescimoPeso + valorAcrescimoDistancia

    if expressa:
        valorBase += valorBase * 0.5

    if cliente_premium:
        valorBase -= valorBase * 0.1

    return round(valorBase, 2)