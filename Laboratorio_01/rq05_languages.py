def process_rq05(repos):
    language_counts = {}
    results = []
    for repo in repos:
        lang = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "None"
        language_counts[lang] = language_counts.get(lang, 0) + 1
        results.append({
            "repository": repo["nameWithOwner"],
            "primary_language": lang,
            "stars": repo["stargazerCount"]
        })
    sorted_langs = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    return {
        "results": results,
        "language_distribution": dict(sorted_langs),
        "top_languages": sorted_langs[:10],
        "total_repos_per_language": language_counts
    }

POPULAR_LANGUAGES_TIOBE = [
    "Python", "C", "C++", "Java", "C#", "JavaScript", "Go",
    "SQL", "R", "Swift", "Rust", "Kotlin", "Ruby", "PHP", "TypeScript"
]

def validate_rq05(repos, sample_size=5):
    sample = repos[:sample_size]
    for repo in sample:
        lang = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "None"
        is_popular = lang in POPULAR_LANGUAGES_TIOBE
        print(f"[RQ05] {repo['nameWithOwner']}: linguagem={lang}, popular_no_tiobe={is_popular}")
    print(f"[RQ05] Validação com {sample_size} repositórios concluída.")