import requests
import sys

def search_github(query):
    url = f"https://api.github.com/search/repositories?q={query}+language:javascript+language:typescript&sort=stars&order=desc"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_game_templates.py <game_type>")
        sys.exit(1)
    
    game_type = sys.argv[1]
    results = search_github(f"{game_type} card game")
    
    print(f"Top 5 GitHub templates for [1m{game_type}[0m:")
    for i, repo in enumerate(results[:5]):
        print(f"{i+1}. [4m{repo["html_url"]}[0m")
        print(f"   [32m★ {repo["stargazers_count"]}[0m | [34m{repo["language"]}[0m | {repo["description"]}")
