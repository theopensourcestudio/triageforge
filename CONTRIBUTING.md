# Contributing

TriageForge welcomes small, evidence-backed improvements.

## Before opening code

Open an issue for substantial changes. Include the maintainer problem, a sample input, desired output, false-positive risks, and whether the feature requires network or write access.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src/triageforge
```

## Contribution rules

- Keep default behaviour read-only and deterministic.
- Do not send repository content to external services without explicit opt-in.
- Do not add secrets, copied private code, telemetry, or hidden network calls.
- Add tests for behaviour changes and false-positive fixes.
- Prefer a focused pull request with a clear rollback path.
- Treat issue bodies, commit messages, patches, and repository files as untrusted input.

Maintainers aim to acknowledge complete reports within seven days, but this is a volunteer project and not a service-level agreement.
