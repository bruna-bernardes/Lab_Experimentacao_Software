import requests
import json
from config import GITHUB_TOKEN, GRAPHQL_URL, NUM_REPOS

def run_query(query, variables=None):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Query failed: {response.status_code} - {response.text}")
    result = response.json()
    if "errors" in result:
        raise Exception(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
    return result

def build_search_query(cursor=None):
    after = f', after: "{cursor}"' if cursor else ""
    return f"""
    query {{
      search(query: "stars:>1 sort:stars", type: REPOSITORY, first: {NUM_REPOS}{after}) {{
        pageInfo {{
          hasNextPage
          endCursor
        }}
        nodes {{
          ... on Repository {{
            nameWithOwner
            createdAt
            updatedAt
            stargazerCount
            primaryLanguage {{
              name
            }}
            pullRequests(states: MERGED) {{
              totalCount
            }}
            releases {{
              totalCount
            }}
            issues {{
              totalCount
            }}
            closedIssues: issues(states: CLOSED) {{
              totalCount
            }}
          }}
        }}
      }}
    }}
    """

def fetch_repos(num_repos=NUM_REPOS):
    all_repos = []
    cursor = None
    while len(all_repos) < num_repos:
        query = build_search_query(cursor)
        result = run_query(query)
        search = result["data"]["search"]
        all_repos.extend(search["nodes"])
        if search["pageInfo"]["hasNextPage"]:
            cursor = search["pageInfo"]["endCursor"]
        else:
            break
    return all_repos[:num_repos]

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("ERRO: Defina a variável de ambiente GITHUB_TOKEN")
        print("Exemplo: export GITHUB_TOKEN=ghp_seutokenaqui")
        exit(1)
    repos = fetch_repos()
    with open("data/raw_repos.json", "w") as f:
        json.dump(repos, f, indent=2)
    print(f"Coletados {len(repos)} repositórios com sucesso!")