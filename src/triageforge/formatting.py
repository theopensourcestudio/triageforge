from __future__ import annotations

import json
from typing import Any

from .models import AuditReport, IssueTriage, PullRequestRisk


def json_output(value: Any) -> str:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return json.dumps(value, indent=2, ensure_ascii=False)


def audit_markdown(report: AuditReport) -> str:
    lines = [
        "# TriageForge repository audit",
        "",
        f"**Score:** {report.score}/{report.max_score} ({report.percentage}%)",
        "",
        "| Check | Status | Points | Detail |",
        "|---|---:|---:|---|",
    ]
    for item in report.findings:
        lines.append(
            f"| {item.check} | {item.status} | {item.points}/{item.max_points} | {item.detail} |"
        )
    return "\n".join(lines) + "\n"


def issue_markdown(result: IssueTriage) -> str:
    lines = [
        "# TriageForge issue report",
        "",
        f"**Priority:** {result.priority}",
        f"**Suggested labels:** {', '.join(result.labels)}",
        "",
        result.maintainer_note,
    ]
    if result.needs_information:
        lines.extend(
            ["", "## Information to request", "", *[f"- {x}" for x in result.needs_information]]
        )
    if result.duplicate_candidates:
        lines.extend(["", "## Possible duplicates", ""])
        for item in result.duplicate_candidates:
            reference = f"#{item.number}" if item.number is not None else item.title
            lines.append(f"- {reference}: {item.title} ({item.similarity:.0%} similarity)")
    if result.ai_note:
        lines.extend(["", "## Optional AI review", "", result.ai_note])
    return "\n".join(lines) + "\n"


def pr_markdown(result: PullRequestRisk) -> str:
    lines = [
        "# TriageForge pull-request risk report",
        "",
        f"**Risk:** {result.level.upper()} ({result.score}/100)",
        f"**Diff:** +{result.additions} / -{result.deletions} across {len(result.files)} files",
    ]
    if result.reasons:
        lines.extend(["", "## Risk signals", "", *[f"- {x}" for x in result.reasons]])
    lines.extend(["", "## Recommended checks", "", *[f"- {x}" for x in result.recommended_checks]])
    if result.ai_note:
        lines.extend(["", "## Optional AI review", "", result.ai_note])
    return "\n".join(lines) + "\n"
