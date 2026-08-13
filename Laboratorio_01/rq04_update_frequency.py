from datetime import datetime

def calculate_days_since_update(updated_at):
    updated = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.utcnow()
    return (now - updated).days

def process_rq04(repos):
    update_days = []
    results = []
    for repo in repos:
        days = calculate_days_since_update(repo["updatedAt"])
        update_days.append(days)
        results.append({
            "repository": repo["nameWithOwner"],
            "updated_at": repo["updatedAt"],
            "days_since_update": days,
            "stars": repo["stargazerCount"]
        })
    update_days.sort()
    median_days = update_days[len(update_days) // 2]
    return {
        "results": results,
        "median_days_since_update": median_days,
        "mean_days_since_update": round(sum(update_days) / len(update_days), 2),
        "min_days": min(update_days),
        "max_days": max(update_days)
    }

def validate_rq04(repos, sample_size=5):
    sample = repos[:sample_size]
    for repo in sample:
        days = calculate_days_since_update(repo["updatedAt"])
        print(f"[RQ04] {repo['nameWithOwner']}: dias desde última atualização={days}, updated_at={repo['updatedAt']}")
    print(f"[RQ04] Validação com {sample_size} repositórios concluída.")