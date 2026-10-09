
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
