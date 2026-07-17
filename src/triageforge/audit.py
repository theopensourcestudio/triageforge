from __future__ import annotations

from pathlib import Path

from .models import AuditReport, Finding


def _exists(root: Path, candidates: tuple[str, ...]) -> bool:
    return any((root / candidate).exists() for candidate in candidates)


def _has_glob(root: Path, patterns: tuple[str, ...]) -> bool:
    return any(any(root.glob(pattern)) for pattern in patterns)


def audit_repository(path: str | Path = ".") -> AuditReport:
    root = Path(path).resolve()
    checks: list[tuple[str, int, bool, str, str]] = [
        (
            "README",
            10,
            _exists(root, ("README.md", "README.rst", "README.txt")),
            "A project overview exists.",
            "Add a README with purpose, installation, examples, and support expectations.",
        ),
        (
            "OSI licence",
            10,
            _exists(root, ("LICENSE", "LICENSE.md", "COPYING")),
            "A licence file exists.",
            "Add an explicit open-source licence such as MIT or Apache-2.0.",
        ),
        (
            "Contributing guide",
            8,
            _exists(root, ("CONTRIBUTING.md", ".github/CONTRIBUTING.md")),
            "Contributor instructions exist.",
            "Explain setup, testing, review, and contribution expectations.",
        ),
        (
            "Code of conduct",
            6,
            _exists(root, ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md")),
            "A code of conduct exists.",
            "Add a community code of conduct and enforcement contact.",
        ),
        (
            "Security policy",
            8,
            _exists(root, ("SECURITY.md", ".github/SECURITY.md")),
            "A vulnerability disclosure policy exists.",
            "Document supported versions and a private reporting route.",
        ),
        (
            "Issue templates",
            6,
            (root / ".github/ISSUE_TEMPLATE").is_dir(),
            "Structured issue templates exist.",
            "Add bug and feature templates that request reproducible evidence.",
        ),
        (
            "Pull-request template",
            5,
            _exists(root, (".github/pull_request_template.md", "PULL_REQUEST_TEMPLATE.md")),
            "A pull-request checklist exists.",
            "Add scope, tests, risk, and documentation checks.",
        ),
        (
            "Continuous integration",
            10,
            _has_glob(root, (".github/workflows/*.yml", ".github/workflows/*.yaml")),
            "Automated workflows exist.",
            "Run tests and static checks on every pull request.",
        ),
        (
            "Automated tests",
            10,
            _has_glob(root, ("tests/test_*.py", "test/**/*.py", "**/*.test.js", "**/*.spec.ts")),
            "A test suite was detected.",
            "Add regression tests for core behaviour and failure paths.",
        ),
        (
            "Dependency updates",
            5,
            _exists(root, (".github/dependabot.yml", ".github/renovate.json", "renovate.json")),
            "Automated dependency updates are configured.",
            "Configure Dependabot or Renovate with a manageable schedule.",
        ),
        (
            "Changelog",
            5,
            _exists(root, ("CHANGELOG.md", "CHANGES.md", "HISTORY.md")),
            "Release history is documented.",
            "Keep a human-readable changelog linked to releases.",
        ),
        (
            "Package metadata",
            7,
            _exists(root, ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml")),
            "Machine-readable package metadata exists.",
            "Add standard metadata so users can install and identify the project.",
        ),
        (
            "Governance",
            5,
            _exists(root, ("GOVERNANCE.md", ".github/GOVERNANCE.md")),
            "Maintainer and decision-making expectations are documented.",
            "Document maintainers, decision rights, and succession expectations.",
        ),
        (
            "Release workflow",
            5,
            _has_glob(root, (".github/workflows/*release*.yml", ".github/workflows/*publish*.yml")),
            "A release-oriented workflow exists.",
            "Automate packaging, checksums, changelog validation, and publishing.",
        ),
    ]

    findings: list[Finding] = []
    for name, weight, passed, detail, remediation in checks:
        findings.append(
            Finding(
                check=name,
                status="pass" if passed else "missing",
                points=weight if passed else 0,
                max_points=weight,
                detail=detail if passed else remediation,
                remediation=None if passed else remediation,
            )
        )

    return AuditReport(
        path=str(root),
        score=sum(item.points for item in findings),
        max_score=sum(item.max_points for item in findings),
        findings=findings,
    )
