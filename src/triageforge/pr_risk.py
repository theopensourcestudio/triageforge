from __future__ import annotations

import subprocess
from pathlib import Path

from .models import FileChange, PullRequestRisk

_SENSITIVE_RULES: tuple[tuple[tuple[str, ...], str, int], ...] = (
    ((".github/workflows/",), "changes CI or release automation", 18),
    (("auth", "login", "permission", "rbac", "oauth"), "touches authentication or permissions", 20),
    (("migrations/", "schema", "database", "db/"), "changes persistent data or migrations", 18),
    (("security", "crypto", "secret", "token"), "touches security-sensitive code", 20),
    (
        ("package-lock.json", "poetry.lock", "uv.lock", "cargo.lock"),
        "updates dependency lock data",
        8,
    ),
    (("public/", "api/", "__init__.py"), "may change a public interface", 10),
)


def _run_git(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _risk_for_path(path: str) -> tuple[list[str], int]:
    lowered = path.lower()
    reasons: list[str] = []
    score = 0
    for needles, reason, points in _SENSITIVE_RULES:
        if any(needle in lowered for needle in needles):
            reasons.append(reason)
            score += points
    if lowered.endswith((".md", ".rst", ".txt")):
        score -= 3
    if "/test" in lowered or lowered.startswith("tests/"):
        score -= 2
    return reasons, max(score, 0)


def analyze_diff(
    path: str | Path = ".", base: str = "HEAD~1", head: str = "HEAD"
) -> PullRequestRisk:
    root = Path(path).resolve()
    output = _run_git(root, ["diff", "--numstat", f"{base}...{head}"])
    files: list[FileChange] = []
    score = 0
    additions = 0
    deletions = 0
    reasons: list[str] = []

    for line in output.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        added_raw, deleted_raw, filename = parts
        added = int(added_raw) if added_raw.isdigit() else 0
        deleted = int(deleted_raw) if deleted_raw.isdigit() else 0
        path_reasons, path_score = _risk_for_path(filename)
        files.append(FileChange(filename, added, deleted, path_reasons))
        additions += added
        deletions += deleted
        score += path_score
        reasons.extend(path_reasons)

    changed_lines = additions + deletions
    file_count = len(files)
    if changed_lines > 1000:
        score += 30
        reasons.append("changes more than 1,000 lines")
    elif changed_lines > 400:
        score += 20
        reasons.append("changes more than 400 lines")
    elif changed_lines > 150:
        score += 10
        reasons.append("changes more than 150 lines")
    if file_count > 30:
        score += 20
        reasons.append("touches more than 30 files")
    elif file_count > 12:
        score += 10
        reasons.append("touches more than 12 files")

    score = min(score, 100)
    level = (
        "low" if score < 20 else "medium" if score < 50 else "high" if score < 75 else "critical"
    )
    checks = ["Run the complete automated test suite."]
    if any("authentication" in reason or "security" in reason for reason in reasons):
        checks.append("Request a security-focused review from a second maintainer.")
    if any("persistent data" in reason for reason in reasons):
        checks.append("Test forward and rollback migration paths on representative data.")
    if any("public interface" in reason for reason in reasons):
        checks.append("Check backwards compatibility and document any breaking change.")
    if changed_lines > 400:
        checks.append("Consider splitting the change into independently reviewable pull requests.")
    if not any(item.path.startswith("tests/") for item in files):
        checks.append("Confirm whether regression tests should accompany this change.")

    return PullRequestRisk(
        level=level,
        score=score,
        additions=additions,
        deletions=deletions,
        files=files,
        reasons=sorted(set(reasons)),
        recommended_checks=checks,
    )
