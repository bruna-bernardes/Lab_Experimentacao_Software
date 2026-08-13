from datetime import datetime

def calculate_age(created_at):
    created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.utcnow()
    age_years = (now - created).days / 365.25
    return round(age_years, 2)

def process_rq01(repos):
    ages = []
    results = []
    for repo in repos:
        age = calculate_age(repo["createdAt"])
        ages.append(age)
        results.append({
            "repository": repo["nameWithOwner"],
            "created_at": repo["createdAt"],
            "age_years": age,
            "stars": repo["stargazerCount"]
        })
    ages.sort()
    median_age = ages[len(ages) // 2]
    return {
        "results": results,
        "median_age_years": median_age,
        "mean_age_years": round(sum(ages) / len(ages), 2),
        "min_age": min(ages),
        "max_age": max(ages)
    }

def validate_rq01(repos, sample_size=5):
    sample = repos[:sample_size]
    for repo in sample:
        age = calculate_age(repo["createdAt"])
        print(f"[RQ01] {repo['nameWithOwner']}: idade={age} anos, criado em={repo['createdAt']}")
    print(f"[RQ01] Validação com {sample_size} repositórios concluída.")