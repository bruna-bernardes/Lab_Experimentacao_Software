import math
from numbers import Real


def avaliar_sla(
    prioridade,
    horas_aberto,
    cliente_vip=False,
    indisponibilidade_total=False
):
    prazos = {
        "baixa": 72.0,
        "media": 48.0,
        "alta": 24.0,
        "critica": 8.0,
    }

    if not isinstance(prioridade, str):
        raise ValueError("prioridade inválida")

    prioridade_normalizada = prioridade.lower()
    if prioridade_normalizada not in prazos:
        raise ValueError("prioridade inválida")

    if (
        isinstance(horas_aberto, bool)
        or not isinstance(horas_aberto, Real)
        or not math.isfinite(horas_aberto)
        or horas_aberto < 0
    ):
        raise ValueError("horas_aberto inválido")

    prazo = prazos[prioridade_normalizada]
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
