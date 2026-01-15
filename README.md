# Manage Brain

Track ideas across GitHub and GitLab repos, keep status in one place, and see
what changed since the last check.

## Project List (edit this)
The script parses this list. Keep the keys as shown.

<!-- PROJECT_LIST_START -->
- name: Polymarket Expectation
  repo: https://github.com/AvrahamRaviv/polymarket-expectation
<!-- PROJECT_LIST_END -->

## Project Status Table (auto-generated)
<!-- PROJECT_TABLE_START -->
| Project | Status | Todo | Last Update |
| --- | --- | --- | --- |
| [Polymarket Expectation](https://github.com/AvrahamRaviv/polymarket-expectation) | wip | - | 2026-01-15 |
<!-- PROJECT_TABLE_END -->

## Latest Changes (auto-generated)
<!-- LATEST_CHANGES_START -->
- Polymarket Expectation: Update README with comprehensive documentation

- Quick start all-in-one command
- Workflow diagram (train → find → evaluate)
- Nested CV with holdout documentation
- Find opportunities command
- Evaluate opportunities command
- Example results output
- Conservative and full grid search examples
- Updated project structure

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (3aa9aae, 2026-01-15)
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
5. Push updates automatically:
   - `python scripts/update_ideas.py --push`

## Collaborator Setup (for your brother)
1. Clone the repo and create a virtualenv:
   - `git clone https://github.com/AvrahamRaviv/manage_brain.git`
   - `cd manage_brain`
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Create API tokens (needed for private repos or higher limits):
   - GitHub: `https://github.com/settings/tokens` (classic token, scope: `repo`)
   - GitLab: `https://gitlab.com/-/profile/personal_access_tokens` (scope: `read_api`)
3. Export tokens in his shell:
   - `export GITHUB_TOKEN=...`
   - `export GITLAB_TOKEN=...`
4. Add his projects and run:
   - `python scripts/update_ideas.py --add "Project Name|https://github.com/owner/repo|todo"`
5. If he wants auto-push too:
   - ensure he is a collaborator with write access
   - `python scripts/update_ideas.py --push`
