from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .duplicate import find_duplicates
from .models import IssueTriage

_LABEL_RULES: dict[str, tuple[str, ...]] = {
    "bug": ("bug", "error", "exception", "crash", "broken", "fails", "failure", "regression"),
    "enhancement": ("feature", "enhancement", "request", "support", "add", "would be useful"),
    "documentation": ("docs", "documentation", "readme", "typo", "example", "tutorial"),
    "security": ("security", "vulnerability", "cve", "exploit", "secret", "credential"),
    "performance": ("slow", "performance", "latency", "memory leak", "cpu", "timeout"),
    "dependencies": ("dependency", "dependencies", "upgrade", "version conflict", "lockfile"),
    "accessibility": ("accessibility", "screen reader", "keyboard", "aria", "contrast"),
    "question": ("how do i", "question", "help", "is it possible", "why does"),
}


def _suggest_labels(text: str) -> list[str]:
    lowered = text.lower()
    labels = [
        label for label, phrases in _LABEL_RULES.items() if any(p in lowered for p in phrases)
    ]
    if not labels:
        labels.append("needs-triage")
    return labels


def _priority(text: str, labels: list[str]) -> str:
    lowered = text.lower()
    if "security" in labels or any(
        term in lowered for term in ("data loss", "remote code", "production down")
    ):
        return "urgent"
    if any(term in lowered for term in ("regression", "crash", "blocks release", "cannot start")):
        return "high"
    if "bug" in labels:
        return "normal"
    return "low"


def _missing_information(title: str, body: str, labels: list[str]) -> list[str]:
    missing: list[str] = []
    lowered = body.lower()
    if len(title.strip()) < 8:
        missing.append("Use a more descriptive title.")
    if len(body.strip()) < 40:
        missing.append("Describe what happened and what you expected.")
    if "bug" in labels:
        if not any(term in lowered for term in ("steps", "reproduce", "reproduction")):
            missing.append("Add minimal reproduction steps.")
        if not any(term in lowered for term in ("version", "commit", "release")):
            missing.append("Include the affected project version or commit.")
        if not any(
            term in lowered
            for term in ("windows", "linux", "macos", "environment", "python", "node")
        ):
            missing.append("Include operating system and runtime details.")
    return missing


def triage_issue(
    title: str,
    body: str,
    existing_issues: Iterable[dict[str, Any]] = (),
) -> IssueTriage:
    text = f"{title}\n{body}"
    labels = _suggest_labels(text)
    missing = _missing_information(title, body, labels)
    duplicates = find_duplicates(title, body, existing_issues)
    note_parts = [
        f"Suggested labels: {', '.join(labels)}.",
        f"Priority: {_priority(text, labels)}.",
    ]
    if duplicates:
        note_parts.append("Review possible duplicates before assigning work.")
    if missing:
        note_parts.append("Request the missing evidence before investigation.")
    return IssueTriage(
        labels=labels,
        priority=_priority(text, labels),
        needs_information=missing,
        duplicate_candidates=duplicates,
        maintainer_note=" ".join(note_parts),
    )
