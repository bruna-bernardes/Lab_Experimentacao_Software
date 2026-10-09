
import calendar
from datetime import datetime, timedelta, timezone


def converter_data(valor):
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def periodos_mensais(inicio, fim):
    inicio = converter_data(inicio)
    fim = converter_data(fim)

    if inicio > fim:
        raise ValueError("A data inicial não pode ser maior que a final.")

    while inicio <= fim:
        ultimo_dia = calendar.monthrange(inicio.year, inicio.month)[1]
        ultimo_instante = datetime(
            inicio.year, inicio.month, ultimo_dia,
            23, 59, 59, tzinfo=timezone.utc
        )
        termino = min(ultimo_instante, fim)

        yield inicio, termino
        inicio = termino + timedelta(seconds=1)


def coletar_workflows(api, repositorio):
    return api.paginas(f"/repos/{repositorio}/actions/workflows")


def coletar_runs(api, repositorio, branch, inicio, fim):
    runs = []
    vistos = set()
    endpoint = f"/repos/{repositorio}/actions/runs"

    def coletar_periodo(data_inicio, data_fim):
        periodo = f"{data_inicio:%Y-%m-%dT%H:%M:%SZ}..{data_fim:%Y-%m-%dT%H:%M:%SZ}"
        parametros = {
            "branch": branch,
            "event": "push",
            "created": periodo,
            "per_page": 100
        }

        primeira = api.get(endpoint, {**parametros, "page": 1})
        total = primeira["data"].get("total_count", 0)

        if total >= 1000:
            segundos = int((data_fim - data_inicio).total_seconds())

            if segundos < 1:
                raise RuntimeError(f"Intervalo mínimo atingido: {periodo}")

            meio = data_inicio + timedelta(seconds=segundos // 2)
            print(f"Dividindo período com {total} runs: {periodo}")

            coletar_periodo(data_inicio, meio)
            coletar_periodo(meio + timedelta(seconds=1), data_fim)
            return

        pagina = 1

        while True:
            resposta = primeira if pagina == 1 else api.get(
                endpoint, {**parametros, "page": pagina}
            )
            lote = resposta["data"].get("workflow_runs", [])

            for run in lote:
                if run.get("id") in vistos:
                    continue

                if run.get("head_branch") != branch or run.get("event") != "push":
                    continue

                data = run.get("created_at")
                if not data:
                    continue

                instante = converter_data(data)
                if not data_inicio <= instante <= data_fim:
                    continue

                vistos.add(run["id"])
                runs.append(run)

            if len(lote) < 100:
                break

            pagina += 1

    for data_inicio, data_fim in periodos_mensais(inicio, fim):
        coletar_periodo(data_inicio, data_fim)

    return runs
