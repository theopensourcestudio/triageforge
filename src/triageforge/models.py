from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    check: str
    status: str
    points: int
    max_points: int
    detail: str
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuditReport:
    path: str
    score: int
    max_score: int
    findings: list[Finding]

    @property
    def percentage(self) -> int:
        if self.max_score == 0:
            return 0
        return round((self.score / self.max_score) * 100)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "findings": [finding.to_dict() for finding in self.findings],
        }


@dataclass(frozen=True)
class DuplicateCandidate:
    number: int | None
    title: str
    similarity: float
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IssueTriage:
    labels: list[str]
    priority: str
    needs_information: list[str]
    duplicate_candidates: list[DuplicateCandidate] = field(default_factory=list)
    maintainer_note: str = ""
    ai_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "labels": self.labels,
            "priority": self.priority,
            "needs_information": self.needs_information,
            "duplicate_candidates": [item.to_dict() for item in self.duplicate_candidates],
            "maintainer_note": self.maintainer_note,
            "ai_note": self.ai_note,
        }


@dataclass(frozen=True)
class FileChange:
    path: str
    additions: int
    deletions: int
    risk_reasons: list[str]

    @property
    def changed_lines(self) -> int:
        return self.additions + self.deletions

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"changed_lines": self.changed_lines}


@dataclass(frozen=True)
class PullRequestRisk:
    level: str
    score: int
    additions: int
    deletions: int
    files: list[FileChange]
    reasons: list[str]
    recommended_checks: list[str]
    ai_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "score": self.score,
            "additions": self.additions,
            "deletions": self.deletions,
            "files": [item.to_dict() for item in self.files],
            "reasons": self.reasons,
            "recommended_checks": self.recommended_checks,
            "ai_note": self.ai_note,
        }
