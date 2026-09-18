def avaliar_sla(
    prioridade,
    horas_aberto,
    cliente_vip=False,
    indisponibilidade_total=False
):
    prioridadeMinuscula = prioridade.lower() if isinstance(prioridade, str) else ""

    if prioridadeMinuscula == "baixa":
        prazo = 72.0
    elif prioridadeMinuscula == "media":
        prazo = 48.0
    elif prioridadeMinuscula == "alta":
        prazo = 24.0
    elif prioridadeMinuscula == "critica":
        prazo = 8.0
    else:
        raise ValueError("Prioridade desconhecida: " + str(prioridade))

    if horas_aberto < 0:
        raise ValueError("horas_aberto nao pode ser negativo")

    if cliente_vip:
        prazo = prazo - (prazo * 0.25)

    if indisponibilidade_total and prazo > 4.0:
        prazo = 4.0

    if horas_aberto > prazo:
        status = "ESTOURADO"
    elif horas_aberto >= prazo * 0.75:
        status = "ATENCAO"
    else:
        status = "DENTRO"

    return {
        "prazo_horas": round(prazo, 2),
        "status": status
    }