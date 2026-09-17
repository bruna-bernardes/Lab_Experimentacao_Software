def calcular_estacionamento(
    minutos,
    fim_de_semana=False,
    mensalista=False
):
    if minutos <= 0 or minutos > 1440:
        raise ValueError("Minutos inválidos.")

    if minutos <= 30:
        valor = 4.00
    elif minutos <= 60:
        valor = 7.00
        
    else:
        tempo_extra = minutos - 60
        blocos = tempo_extra // 30
        if tempo_extra % 30 != 0:
            blocos += 1
        valor = 7.00 + (blocos * 3.00)
    
    if valor > 35.00:
        valor = 35.00
        
    if fim_de_semana:
        valor = valor * 1.20
        
    if mensalista:
        valor = valor * 0.75
        
    return round(valor, 2)