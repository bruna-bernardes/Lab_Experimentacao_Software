def avaliar_sla(
    prioridade,
    horas_aberto,
    cliente_vip=False,
    indisponibilidade_total=False
):
    prazos = {
        "baixa": 72,
        "media": 48,
        "alta": 24,
        "critica": 8,
    }

    if not isinstance(prioridade, str):
        raise ValueError("Prioridade inválida.")

    prioridade_normalizada = prioridade.lower()

    if prioridade_normalizada not in prazos:
        raise ValueError("Prioridade inválida.")

    if not isinstance(horas_aberto, (int, float)) or horas_aberto < 0:
        raise ValueError("Horas em aberto inválidas.")

    prazo = float(prazos[prioridade_normalizada])

    if cliente_vip:
        prazo *= 0.75

    if indisponibilidade_total:
        prazo = min(prazo, 4.0)

    if horas_aberto > prazo:
        status = "ESTOURADO"
    elif horas_aberto >= prazo * 0.75:
        status = "ATENCAO"
    else:
        status = "DENTRO"

    return {
        "prazo_horas": round(prazo, 2),
        "status": status,
    }
