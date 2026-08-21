import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GRAPHQL_URL = "https://api.github.com/graphql"

NUM_REPOS = 1000
PAGE_SIZE = 10

VALIDATION_SAMPLE_SIZE = 5