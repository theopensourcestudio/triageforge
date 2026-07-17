from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

from .ai import AIUnavailable, enrich_with_openai
from .audit import audit_repository
from .formatting import audit_markdown, issue_markdown, json_output, pr_markdown
from .github_event import handle_event
from .pr_risk import analyze_diff
from .release_notes import generate_release_notes
from .triage import triage_issue


def _load_issues(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(value, dict) and "issues" in value:
        value = value["issues"]
    if not isinstance(value, list):
        raise ValueError("Issues JSON must be a list or an object containing an 'issues' list.")
    return [item for item in value if isinstance(item, dict)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="triageforge",
        description="Practical maintainer automation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit repository community and maintenance readiness.")
    audit.add_argument("path", nargs="?", default=".")
    audit.add_argument("--json", action="store_true")
    audit.add_argument("--fail-under", type=int, default=0, metavar="PERCENT")

    issue = sub.add_parser("issue", help="Triage an issue and find possible duplicates.")
    issue.add_argument("--title", required=True)
    issue.add_argument("--body", default="")
    issue.add_argument("--issues-json")
    issue.add_argument("--ai", action="store_true")
    issue.add_argument("--model")
    issue.add_argument("--json", action="store_true")

    pr = sub.add_parser("pr", help="Score pull-request risk from a local git diff.")
    pr.add_argument("path", nargs="?", default=".")
    pr.add_argument("--base", default="HEAD~1")
    pr.add_argument("--head", default="HEAD")
    pr.add_argument("--ai", action="store_true")
    pr.add_argument("--model")
    pr.add_argument("--json", action="store_true")

    release = sub.add_parser("release", help="Generate release notes from git history.")
    release.add_argument("path", nargs="?", default=".")
    release.add_argument("--from-ref")
    release.add_argument("--to-ref", default="HEAD")
    release.add_argument("--output")

    event = sub.add_parser("event", help="Handle a GitHub issue or pull-request event payload.")
    event.add_argument("--event-path", required=True)
    event.add_argument("--repository", default=".")
    event.add_argument("--ai", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            audit_result = audit_repository(args.path)
            print(json_output(audit_result) if args.json else audit_markdown(audit_result))
            return 1 if audit_result.percentage < args.fail_under else 0

        if args.command == "issue":
            issue_result = triage_issue(
                args.title,
                args.body,
                _load_issues(args.issues_json),
            )
            if args.ai:
                try:
                    ai_note = enrich_with_openai(
                        "Review an issue triage result",
                        json_output(issue_result),
                        model=args.model,
                    )
                except AIUnavailable as exc:
                    ai_note = str(exc)
                issue_result = replace(issue_result, ai_note=ai_note)
            print(json_output(issue_result) if args.json else issue_markdown(issue_result))
            return 0

        if args.command == "pr":
            pr_result = analyze_diff(args.path, args.base, args.head)
            if args.ai:
                try:
                    ai_note = enrich_with_openai(
                        "Review a pull-request risk report",
                        json_output(pr_result),
                        model=args.model,
                    )
                except AIUnavailable as exc:
                    ai_note = str(exc)
                pr_result = replace(pr_result, ai_note=ai_note)
            print(json_output(pr_result) if args.json else pr_markdown(pr_result))
            return 0

        if args.command == "release":
            notes = generate_release_notes(args.path, args.from_ref, args.to_ref)
            if args.output:
                Path(args.output).write_text(notes, encoding="utf-8")
            else:
                print(notes)
            return 0

        if args.command == "event":
            print(handle_event(args.event_path, args.repository, args.ai))
            return 0

        return 2
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"triageforge: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
