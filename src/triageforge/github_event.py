from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any

from .ai import AIUnavailable, enrich_with_openai
from .formatting import issue_markdown, pr_markdown
from .pr_risk import analyze_diff
from .triage import triage_issue


def _append_summary(markdown: str) -> None:
    destination = os.environ.get("GITHUB_STEP_SUMMARY")
    if destination:
        with Path(destination).open("a", encoding="utf-8") as handle:
            handle.write(markdown + "\n")


def _set_output(name: str, value: str) -> None:
    destination = os.environ.get("GITHUB_OUTPUT")
    if destination:
        safe = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        with Path(destination).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={safe}\n")


def handle_event(
    event_path: str | Path,
    repository_path: str | Path = ".",
    use_ai: bool = False,
) -> str:
    payload: dict[str, Any] = json.loads(Path(event_path).read_text(encoding="utf-8"))

    if "issue" in payload:
        issue = payload["issue"]
        issue_result = triage_issue(
            str(issue.get("title", "")),
            str(issue.get("body") or ""),
        )
        if use_ai:
            try:
                ai_note = enrich_with_openai(
                    "Review this issue triage",
                    json.dumps(issue_result.to_dict()),
                )
            except AIUnavailable as exc:
                ai_note = str(exc)
            issue_result = replace(issue_result, ai_note=ai_note)

        markdown = issue_markdown(issue_result)
        _set_output("labels", ",".join(issue_result.labels))
        _set_output("priority", issue_result.priority)

    elif "pull_request" in payload:
        pull = payload["pull_request"]
        base = str(pull.get("base", {}).get("sha", "HEAD~1"))
        head = str(pull.get("head", {}).get("sha", "HEAD"))
        pr_result = analyze_diff(repository_path, base, head)
        if use_ai:
            try:
                ai_note = enrich_with_openai(
                    "Review this pull-request risk report",
                    json.dumps(pr_result.to_dict()),
                )
            except AIUnavailable as exc:
                ai_note = str(exc)
            pr_result = replace(pr_result, ai_note=ai_note)

        markdown = pr_markdown(pr_result)
        _set_output("risk_level", pr_result.level)
        _set_output("risk_score", str(pr_result.score))

    else:
        raise ValueError("Unsupported event: expected an issue or pull_request payload.")

    _append_summary(markdown)
    return markdown
