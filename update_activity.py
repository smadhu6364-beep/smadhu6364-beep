"""
Pulls recent public GitHub activity for the profile owner and writes it into
README.md between the START_SECTION/END_SECTION markers. Runs on a schedule
via .github/workflows/update-activity.yml (and on manual dispatch). Uses only
the standard library so the workflow needs no dependency install step.
"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

USERNAME = "smadhu6364-beep"
API_URL = f"https://api.github.com/users/{USERNAME}/events/public"
README_PATH = "README.md"
START = "<!--START_SECTION:activity-->"
END = "<!--END_SECTION:activity-->"
MAX_ITEMS = 5

EVENT_ICONS = {
    "PushEvent": "\U0001F528",
    "CreateEvent": "\U0001F331",
    "PullRequestEvent": "\U0001F500",
    "IssuesEvent": "\U0001F41B",
    "IssueCommentEvent": "\U0001F4AC",
    "WatchEvent": "⭐",
    "ForkEvent": "\U0001F374",
    "ReleaseEvent": "\U0001F680",
    "PublicEvent": "\U0001F513",
}


def fetch_events():
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": USERNAME, "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def describe(event):
    etype = event.get("type")
    repo = event.get("repo", {}).get("name", "")
    repo_link = f"[`{repo}`](https://github.com/{repo})"
    icon = EVENT_ICONS.get(etype, "\U0001F4CC")
    payload = event.get("payload", {})

    if etype == "PushEvent":
        n = len(payload.get("commits", []))
        word = "commit" if n == 1 else "commits"
        return f"{icon} Pushed {n} {word} to {repo_link}"
    if etype == "CreateEvent":
        ref_type = payload.get("ref_type", "repository")
        if ref_type == "repository":
            return f"{icon} Created repository {repo_link}"
        ref = payload.get("ref", "")
        return f"{icon} Created {ref_type} `{ref}` in {repo_link}"
    if etype == "PullRequestEvent":
        action = payload.get("action", "").capitalize()
        num = payload.get("number", "")
        return f"{icon} {action} pull request [`#{num}`](https://github.com/{repo}/pull/{num}) in {repo_link}"
    if etype == "IssuesEvent":
        action = payload.get("action", "").capitalize()
        num = payload.get("issue", {}).get("number", "")
        return f"{icon} {action} issue [`#{num}`](https://github.com/{repo}/issues/{num}) in {repo_link}"
    if etype == "WatchEvent":
        return f"{icon} Starred {repo_link}"
    if etype == "ForkEvent":
        return f"{icon} Forked {repo_link}"
    if etype == "ReleaseEvent":
        tag = payload.get("release", {}).get("tag_name", "")
        return f"{icon} Released `{tag}` on {repo_link}"
    return f"{icon} {etype} on {repo_link}"


def build_block(events):
    lines = []
    seen = set()
    for e in events:
        if e.get("type") not in EVENT_ICONS:
            continue
        line = describe(e)
        if line in seen:
            continue
        seen.add(line)
        lines.append(f"- {line}")
        if len(lines) >= MAX_ITEMS:
            break

    if not lines:
        lines = ["- No public activity in the last 90 days. Check back soon."]

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return "\n".join(lines) + f"\n\n_Last updated {stamp}_"


def main():
    try:
        events = fetch_events()
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Could not fetch events: {exc}")
        return

    block = build_block(events)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START not in content or END not in content:
        raise SystemExit(f"Markers {START} / {END} not found in {README_PATH}")

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    content = pattern.sub(f"{START}\n{block}\n{END}", content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
