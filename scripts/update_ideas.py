#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import sys
from urllib.parse import quote, urlparse

import requests


PROJECT_LIST_START = "<!-- PROJECT_LIST_START -->"
PROJECT_LIST_END = "<!-- PROJECT_LIST_END -->"
PROJECT_TABLE_START = "<!-- PROJECT_TABLE_START -->"
PROJECT_TABLE_END = "<!-- PROJECT_TABLE_END -->"
LATEST_CHANGES_START = "<!-- LATEST_CHANGES_START -->"
LATEST_CHANGES_END = "<!-- LATEST_CHANGES_END -->"

STATUS_NOT_STARTED = "not_started"
STATUS_WIP = "wip"
STATUS_FINISHED = "finished"

RECENT_DAYS_WIP = 30


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"projects": {}}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")


def parse_project_list(readme_text: str) -> list:
    lines = readme_text.splitlines()
    try:
        start_idx = lines.index(PROJECT_LIST_START) + 1
        end_idx = lines.index(PROJECT_LIST_END)
    except ValueError:
        raise ValueError("Project list markers not found in README.")

    projects = []
    current = None
    for line in lines[start_idx:end_idx]:
        if not line.strip():
            continue
        name_match = re.match(r"\s*-\s*name:\s*(.+)\s*$", line)
        if name_match:
            if current:
                projects.append(current)
            current = {"name": name_match.group(1).strip()}
            continue
        if current is None:
            continue
        repo_match = re.match(r"\s*repo:\s*(.+)\s*$", line)
        if repo_match:
            current["repo"] = repo_match.group(1).strip()
            continue
        todo_match = re.match(r"\s*todo:\s*(.*)\s*$", line)
        if todo_match:
            current["todo"] = todo_match.group(1).strip()
            continue

    if current:
        projects.append(current)

    for project in projects:
        if "repo" not in project:
            raise ValueError(f"Missing repo for project: {project.get('name')}")
        project.setdefault("todo", "")

    return projects


def replace_section(text: str, start_marker: str, end_marker: str, new_lines: list) -> str:
    lines = text.splitlines()
    try:
        start_idx = lines.index(start_marker)
        end_idx = lines.index(end_marker)
    except ValueError:
        raise ValueError(f"Markers not found: {start_marker} / {end_marker}")
    if start_idx >= end_idx:
        raise ValueError(f"Invalid marker order: {start_marker} / {end_marker}")

    updated = lines[: start_idx + 1]
    updated.extend(new_lines)
    updated.extend(lines[end_idx:])
    return "\n".join(updated) + "\n"


def parse_repo_url(repo_url: str) -> dict:
    parsed = urlparse(repo_url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if host.endswith("github.com"):
        parts = path.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
        return {"provider": "github", "owner": parts[0], "repo": parts[1], "host": host}
    if host.endswith("gitlab.com"):
        if not path:
            raise ValueError(f"Invalid GitLab repo URL: {repo_url}")
        return {"provider": "gitlab", "path": path, "host": host}
    raise ValueError(f"Unsupported repo host: {repo_url}")


def github_headers(token: str | None) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def gitlab_headers(token: str | None) -> dict:
    headers = {}
    if token:
        headers["PRIVATE-TOKEN"] = token
    return headers


def iso_to_datetime(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def datetime_to_iso(value: dt.datetime | None) -> str:
    if not value:
        return "-"
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%d")


def compute_status(has_release: bool, archived: bool, last_commit_dt: dt.datetime | None) -> str:
    if archived or has_release:
        return STATUS_FINISHED
    if not last_commit_dt:
        return STATUS_NOT_STARTED
    now = dt.datetime.now(dt.timezone.utc)
    if (now - last_commit_dt).days <= RECENT_DAYS_WIP:
        return STATUS_WIP
    return STATUS_NOT_STARTED


def fetch_github_project(repo_url: str, owner: str, repo: str, token: str | None) -> dict:
    api_base = "https://api.github.com"
    repo_resp = requests.get(
        f"{api_base}/repos/{owner}/{repo}",
        headers=github_headers(token),
        timeout=20,
    )
    if repo_resp.status_code == 404:
        raise ValueError(f"GitHub repo not found: {repo_url}")
    repo_resp.raise_for_status()
    repo_data = repo_resp.json()
    default_branch = repo_data.get("default_branch", "main")
    archived = bool(repo_data.get("archived"))

    commits_resp = requests.get(
        f"{api_base}/repos/{owner}/{repo}/commits",
        params={"sha": default_branch, "per_page": 1},
        headers=github_headers(token),
        timeout=20,
    )
    if commits_resp.status_code == 409:
        commits = []
    else:
        commits_resp.raise_for_status()
        commits = commits_resp.json()

    latest_commit = commits[0] if commits else None
    latest_sha = latest_commit.get("sha") if latest_commit else None
    commit_info = latest_commit.get("commit", {}) if latest_commit else {}
    latest_message = commit_info.get("message") if latest_commit else None
    latest_date = iso_to_datetime(
        (commit_info.get("committer") or {}).get("date")
    )

    release_resp = requests.get(
        f"{api_base}/repos/{owner}/{repo}/releases/latest",
        headers=github_headers(token),
        timeout=20,
    )
    has_release = release_resp.status_code == 200

    return {
        "provider": "github",
        "default_branch": default_branch,
        "archived": archived,
        "latest_sha": latest_sha,
        "latest_message": latest_message,
        "latest_date": latest_date,
        "has_release": has_release,
    }


def fetch_gitlab_project(repo_url: str, path: str, token: str | None) -> dict:
    api_base = "https://gitlab.com/api/v4"
    encoded_path = quote(path, safe="")
    repo_resp = requests.get(
        f"{api_base}/projects/{encoded_path}",
        headers=gitlab_headers(token),
        timeout=20,
    )
    if repo_resp.status_code == 404:
        raise ValueError(f"GitLab repo not found: {repo_url}")
    repo_resp.raise_for_status()
    repo_data = repo_resp.json()
    project_id = repo_data.get("id")
    default_branch = repo_data.get("default_branch", "main")
    archived = bool(repo_data.get("archived"))

    commits_resp = requests.get(
        f"{api_base}/projects/{project_id}/repository/commits",
        params={"ref_name": default_branch, "per_page": 1},
        headers=gitlab_headers(token),
        timeout=20,
    )
    commits_resp.raise_for_status()
    commits = commits_resp.json()
    latest_commit = commits[0] if commits else None
    latest_sha = latest_commit.get("id") if latest_commit else None
    latest_message = latest_commit.get("title") if latest_commit else None
    latest_date = iso_to_datetime(latest_commit.get("committed_date") if latest_commit else None)

    releases_resp = requests.get(
        f"{api_base}/projects/{project_id}/releases",
        params={"per_page": 1},
        headers=gitlab_headers(token),
        timeout=20,
    )
    has_release = releases_resp.status_code == 200 and bool(releases_resp.json())

    return {
        "provider": "gitlab",
        "default_branch": default_branch,
        "archived": archived,
        "latest_sha": latest_sha,
        "latest_message": latest_message,
        "latest_date": latest_date,
        "has_release": has_release,
    }


def fetch_project(project: dict, github_token: str | None, gitlab_token: str | None) -> dict:
    parsed = parse_repo_url(project["repo"])
    if parsed["provider"] == "github":
        info = fetch_github_project(project["repo"], parsed["owner"], parsed["repo"], github_token)
    else:
        info = fetch_gitlab_project(project["repo"], parsed["path"], gitlab_token)
    info["repo_url"] = project["repo"]
    return info


def format_table(project_rows: list) -> list:
    lines = [
        "| Project | Status | Todo | Last Update |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(project_rows)
    return lines


def format_project_row(project: dict, status: str, last_update: str) -> str:
    name = project["name"].strip()
    repo_url = project["repo"].strip()
    todo = project.get("todo", "").strip() or "-"
    return f"| [{name}]({repo_url}) | {status} | {todo} | {last_update} |"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Manage Brain README.")
    parser.add_argument("--readme", default="README.md", help="Path to README.md")
    parser.add_argument("--state", default="data/state.json", help="Path to state.json")
    args = parser.parse_args()

    readme_text = read_text(args.readme)
    projects = parse_project_list(readme_text)
    state = load_state(args.state)
    state_projects = state.setdefault("projects", {})

    github_token = os.getenv("GITHUB_TOKEN")
    gitlab_token = os.getenv("GITLAB_TOKEN")

    table_rows = []
    change_lines = []

    for project in projects:
        info = fetch_project(project, github_token, gitlab_token)
        status = compute_status(info["has_release"], info["archived"], info["latest_date"])
        last_update = datetime_to_iso(info["latest_date"])

        table_rows.append(format_project_row(project, status, last_update))

        key = project["repo"]
        prev = state_projects.get(key, {})
        if info["latest_sha"] and info["latest_sha"] != prev.get("latest_sha"):
            short_sha = info["latest_sha"][:7]
            message = info.get("latest_message") or "New commit"
            change_lines.append(f"- {project['name']}: {message} ({short_sha}, {last_update})")

        state_projects[key] = {
            "name": project["name"],
            "repo": project["repo"],
            "latest_sha": info["latest_sha"],
            "latest_date": info["latest_date"].isoformat() if info["latest_date"] else None,
            "status": status,
        }

    if not change_lines:
        change_lines = ["- No changes since last run."]

    updated = replace_section(readme_text, PROJECT_TABLE_START, PROJECT_TABLE_END, format_table(table_rows))
    updated = replace_section(updated, LATEST_CHANGES_START, LATEST_CHANGES_END, change_lines)
    write_text(args.readme, updated)
    save_state(args.state, state)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
