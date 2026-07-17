from __future__ import annotations

import re
import subprocess
from collections import defaultdict
from pathlib import Path

_SECTION_MAP = {
    "feat": "Features",
    "fix": "Fixes",
    "perf": "Performance",
    "docs": "Documentation",
    "refactor": "Internal improvements",
    "test": "Tests",
    "build": "Build and dependencies",
    "ci": "Continuous integration",
    "chore": "Maintenance",
}


def _git_log(root: Path, revision_range: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), "log", "--pretty=format:%h%x09%s", revision_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def generate_release_notes(
    path: str | Path = ".",
    from_ref: str | None = None,
    to_ref: str = "HEAD",
) -> str:
    root = Path(path).resolve()
    revision_range = f"{from_ref}..{to_ref}" if from_ref else to_ref
    sections: dict[str, list[str]] = defaultdict(list)
    for line in _git_log(root, revision_range):
        commit, subject = line.split("\t", 1)
        match = re.match(
            r"(?P<type>[a-zA-Z]+)(?:\([^)]+\))?(?P<breaking>!)?:\s*(?P<title>.+)", subject
        )
        if match:
            section = (
                "Breaking changes"
                if match.group("breaking")
                else _SECTION_MAP.get(match.group("type").lower(), "Other changes")
            )
            title = match.group("title")
        else:
            section = "Other changes"
            title = subject
        sections[section].append(f"- {title} (`{commit}`)")

    preferred_order = [
        "Breaking changes",
        "Features",
        "Fixes",
        "Performance",
        "Documentation",
        "Build and dependencies",
        "Continuous integration",
        "Tests",
        "Maintenance",
        "Internal improvements",
        "Other changes",
    ]
    output = ["# Release notes", ""]
    if not sections:
        return "# Release notes\n\nNo commits were found in the selected range.\n"
    for section in preferred_order:
        entries = sections.get(section)
        if entries:
            output.extend([f"## {section}", "", *entries, ""])
    return "\n".join(output).rstrip() + "\n"
