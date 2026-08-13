import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GRAPHQL_URL = "https://api.github.com/graphql"
NUM_REPOS = 100
VALIDATION_SAMPLE_SIZE = 5