import json, re, urllib.request
from datetime import datetime, timezone

REPOS_PATH = "docs/repos/repos.json"
README_PATH = "README.md"
BASE = "https://github.com/"

def get_package_count(repo_id):
    author, name = repo_id.split("__", 1)
    raw_url = f"https://raw.githubusercontent.com/{author}/{name}/main/docs/repos/{repo_id}/metadata/repo.json"
    # Fall back to local file
    try:
        local = f"docs/repos/{repo_id}/metadata/repo.json"
        with open(local) as f:
            return len(json.load(f))
    except Exception:
        return None

with open(REPOS_PATH) as f:
    repos = json.load(f)

lines = []
for repo_id in repos:
    author, name = repo_id.split("__", 1)
    count = get_package_count(repo_id)
    count_str = f" — {count} packages" if count else ""
    lines.append(f"- [{author}/{name}]({BASE}{author}/{name}){count_str}")

updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
block = "\n".join(lines) + f"\n\n_Last updated: {updated}_"

with open(README_PATH) as f:
    readme = f.read()

new_readme = re.sub(
    r"<!-- TRACKED_REPOS_START -->.*?<!-- TRACKED_REPOS_END -->",
    f"<!-- TRACKED_REPOS_START -->\n{block}\n<!-- TRACKED_REPOS_END -->",
    readme,
    flags=re.DOTALL
)

with open(README_PATH, "w") as f:
    f.write(new_readme)

print(f"Updated README with {len(repos)} repos.")