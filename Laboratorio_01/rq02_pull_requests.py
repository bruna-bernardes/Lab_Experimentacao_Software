def process_rq02(repos):
    pr_counts = []
    results = []
    for repo in repos:
        total_pr = repo["pullRequests"]["totalCount"]
        pr_counts.append(total_pr)
        results.append({
            "repository": repo["nameWithOwner"],
            "merged_prs": total_pr,
            "stars": repo["stargazerCount"]
        })
    pr_counts.sort()
    median_pr = pr_counts[len(pr_counts) // 2]
    return {
        "results": results,
        "median_merged_prs": median_pr,
        "mean_merged_prs": round(sum(pr_counts) / len(pr_counts), 2),
        "min_prs": min(pr_counts),
        "max_prs": max(pr_counts)
    }

def validate_rq02(repos, sample_size=5):
    sample = repos[:sample_size]
    for repo in sample:
        total_pr = repo["pullRequests"]["totalCount"]
        print(f"[RQ02] {repo['nameWithOwner']}: PRs aceitas={total_pr}, estrelas={repo['stargazerCount']}")
    print(f"[RQ02] Validação com {sample_size} repositórios concluída.")