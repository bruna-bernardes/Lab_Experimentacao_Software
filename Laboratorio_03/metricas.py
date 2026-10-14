from datetime import datetime
from statistics import median


def data_hora(valor):
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def lead_time_por_release(releases):
    tempos = []

    for release in releases:
        publicacao = data_hora(release["published_at"])
        datas = []

        for item in release["commits"]:
            autor = item.get("commit", {}).get("author", {})
            if autor.get("date"):
                datas.append(data_hora(autor["date"]))

        if datas:
            horas = (publicacao - min(datas)).total_seconds() / 3600
            if horas >= 0:
                tempos.append(horas)

    return median(tempos) if tempos else None


def lead_time_por_commit(releases):
    tempos = []

    for release in releases:
        publicacao = data_hora(release["published_at"])

        for item in release["commits"]:
            autor = item.get("commit", {}).get("author", {})
            if not autor.get("date"):
                continue

            horas = (publicacao - data_hora(autor["date"])).total_seconds() / 3600

            if horas >= 0:
                tempos.append(horas)

    return median(tempos) if tempos else None


def calcular_cfr_ci(runs):
    falhas = {"failure", "timed_out", "startup_failure"}
    sucessos = {"success"}

    validas = [r for r in runs if r.get("conclusion") in falhas | sucessos]

    if not validas:
        return None

    total_falhas = sum(r["conclusion"] in falhas for r in validas)
    return total_falhas / len(validas)


def calcular_recuperacao(runs):
    from collections import defaultdict

    falhas = {"failure", "timed_out", "startup_failure"}
    grupos = defaultdict(list)

    for run in runs:
        if run.get("conclusion") not in falhas | {"success"}:
            continue
        grupos[run["workflow_id"]].append(run)

    tempos = []
    censurados = 0

    for workflow_runs in grupos.values():
        workflow_runs.sort(key=lambda r: r["run_started_at"])
        inicio_falha = None
        houve_sucesso = False

        for run in workflow_runs:
            conclusao = run["conclusion"]

            if conclusao == "success":
                houve_sucesso = True

                if inicio_falha:
                    termino = data_hora(run["updated_at"])
                    horas = (termino - inicio_falha).total_seconds() / 3600
                    if horas >= 0:
                        tempos.append(horas)
                    inicio_falha = None

            elif houve_sucesso and inicio_falha is None:
                inicio_falha = data_hora(run["run_started_at"])

        if inicio_falha:
            censurados += 1

    return {
        "mediana_horas": median(tempos) if tempos else None,
        "episodios_recuperados": len(tempos),
        "episodios_censurados": censurados,
        "proporcao_censura": censurados / (len(tempos) + censurados)
        if tempos or censurados else None
    }


# --- Sprint 2 (Lab03S02) ------------------------------------------------------

def deployment_frequency(n_releases, inicio, fim):
    """RQ 01: releases publicadas por semana. Semanas = duração da janela em
    dias / 7 (≈ 52,1 para uma janela de 12 meses)."""
    semanas = (data_hora(fim) - data_hora(inicio)).total_seconds() / (7 * 24 * 3600)

    if semanas <= 0:
        raise ValueError("A janela de observação precisa ter duração positiva.")

    return n_releases / semanas


def calcular_cfr_entrega(releases, classificar, inicio, fim, dias=7):
    """RQ 03 (b): proporção de releases seguidas, em até ``dias``, por uma
    release corretiva.

    ``releases``: releases publicadas (sem drafts e sem pré-releases) com
    ``published_at``, em qualquer ordem; podem incluir releases fora da janela.
    ``classificar(anterior, atual)``: devolve True se ``atual`` é corretiva.

    Regra adotada: a release R da janela falha quando a release imediatamente
    seguinte R' é publicada em até ``dias`` dias depois de R **e** é corretiva.
    Releases publicadas nos últimos ``dias`` dias da janela são censuradas
    (ficam fora do denominador).
    """
    from datetime import timedelta

    inicio_dt, fim_dt = data_hora(inicio), data_hora(fim)
    limite_avaliacao = fim_dt - timedelta(days=dias)
    prazo = timedelta(days=dias)

    ordenadas = sorted(releases, key=lambda r: data_hora(r["published_at"]))
    avaliadas = falhas = censuradas = 0

    for indice, release in enumerate(ordenadas):
        publicada = data_hora(release["published_at"])

        if not inicio_dt <= publicada <= fim_dt:
            continue

        if publicada > limite_avaliacao:
            censuradas += 1
            continue

        avaliadas += 1

        if indice + 1 >= len(ordenadas):
            continue

        seguinte = ordenadas[indice + 1]
        intervalo = data_hora(seguinte["published_at"]) - publicada

        if intervalo <= prazo and classificar(release, seguinte):
            falhas += 1

    return {
        "cfr": falhas / avaliadas if avaliadas else None,
        "avaliadas": avaliadas,
        "falhas": falhas,
        "censuradas": censuradas
    }