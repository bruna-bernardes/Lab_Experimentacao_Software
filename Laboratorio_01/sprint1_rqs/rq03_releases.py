def process_rq03(repos):
    release_counts = []
    results = []
    for repo in repos:
        total_releases = repo["releases"]["totalCount"]
        release_counts.append(total_releases)
        results.append({
            "repository": repo["nameWithOwner"],
            "total_releases": total_releases,
            "stars": repo["stargazerCount"]
        })
    release_counts.sort()
    median_releases = release_counts[len(release_counts) // 2]
    return {
        "results": results,
        "median_releases": median_releases,
        "mean_releases": round(sum(release_counts) / len(release_counts), 2),
        "min_releases": min(release_counts),
        "max_releases": max(release_counts)
    }

def validate_rq03(repos, sample_size=5):
    sample = repos[:sample_size]
    for repo in sample:
        total_releases = repo["releases"]["totalCount"]
        print(f"[RQ03] {repo['nameWithOwner']}: releases={total_releases}, estrelas={repo['stargazerCount']}")
    print(f"[RQ03] Validação com {sample_size} repositórios concluída.")