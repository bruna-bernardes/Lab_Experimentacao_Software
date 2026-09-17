import math


def calcular_estacionamento(
    minutos,
    fim_de_semana=False,
    mensalista=False
):
    if isinstance(minutos, bool):
        raise ValueError("minutos deve ser um número entre 1 e 1440")

    try:
        minutos = float(minutos)
    except (TypeError, ValueError):
        raise ValueError("minutos deve ser um número entre 1 e 1440")

    if not 0 < minutos <= 1440:
        raise ValueError("minutos deve ser um número entre 1 e 1440")

    if minutos <= 30:
        valor = 4.00
    elif minutos <= 60:
        valor = 7.00
    else:
        blocos_adicionais = math.ceil((minutos - 60) / 30)
        valor = 7.00 + 3.00 * blocos_adicionais

    valor = min(valor, 35.00)

    if fim_de_semana:
        valor *= 1.20

    if mensalista:
        valor *= 0.75

    return round(valor, 2)
