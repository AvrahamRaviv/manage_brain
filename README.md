# Manage Brain

Track ideas across GitHub and GitLab repos, keep status in one place, and see
what changed since the last check.

## Project List (edit this)
The script parses this list. Keep the keys as shown.

<!-- PROJECT_LIST_START -->
- name: Example Project
  repo: https://github.com/owner/example-project
  todo: write initial spec; decide MVP scope
<!-- PROJECT_LIST_END -->

## Project Status Table (auto-generated)
<!-- PROJECT_TABLE_START -->
| Project | Status | Todo | Last Update |
| --- | --- | --- | --- |
| Example Project | not_started | write initial spec; decide MVP scope | - |
<!-- PROJECT_TABLE_END -->

## Latest Changes (auto-generated)
<!-- LATEST_CHANGES_START -->
- No updates yet.
<!-- LATEST_CHANGES_END -->

## Usage
1. Install dependencies:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Set API tokens (recommended for private repos and higher rate limits):
   - `export GITHUB_TOKEN=...`
   - `export GITLAB_TOKEN=...`
3. Run the updater:
   - `python scripts/update_ideas.py`
4. Add a new project without editing the README:
   - `python scripts/update_ideas.py --add "My Project|https://github.com/me/my-project|first steps"`
