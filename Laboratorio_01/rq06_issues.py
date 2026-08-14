def process_rq06(repos):
    ratios = []
    results = []
    for repo in repos:
        total_issues = repo["issues"]["totalCount"]
        closed_issues = repo["closedIssues"]["totalCount"]
        ratio = closed_issues / total_issues if total_issues > 0 else 0.0
        ratios.append(ratio)
        results.append({
            "repository": repo["nameWithOwner"],
            "total_issues": total_issues,
            "closed_issues": closed_issues,
            "closed_ratio": round(ratio, 4),
            "stars": repo["stargazerCount"]
        })
    ratios.sort()
    median_ratio = ratios[len(ratios) // 2]
    return {
        "results": results,
        "median_closed_ratio": round(median_ratio, 4),
        "mean_closed_ratio": round(sum(ratios) / len(ratios), 4),
        "min_ratio": round(min(ratios), 4),
        "max_ratio": round(max(ratios), 4)
    }

def validate_rq06(repos, sample_size=5):
    sample = repos[:sample_size]
    for repo in sample:
        total_issues = repo["issues"]["totalCount"]
        closed_issues = repo["closedIssues"]["totalCount"]
        ratio = closed_issues / total_issues if total_issues > 0 else 0.0
        print(f"[RQ06] {repo['nameWithOwner']}: issues={total_issues}, fechadas={closed_issues}, razão={ratio:.4f}")
    print(f"[RQ06] Validação com {sample_size} repositórios concluída.")