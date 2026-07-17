# TriageForge

**Local-first maintainer automation for healthier open-source projects.**

TriageForge helps maintainers handle four repetitive jobs without handing control of the repository to a bot:

- audit repository health and community readiness;
- classify issues and flag missing reproduction evidence;
- find likely duplicate issues using an offline similarity engine;
- score pull-request risk from the actual git diff;
- generate readable release notes from conventional or ordinary commits;
- optionally ask OpenAI for a concise second opinion while keeping all writes human-controlled.

The default mode is deterministic, offline, and read-only. AI support is optional. TriageForge never merges code, closes issues, publishes releases, or follows instructions embedded inside issue text.

## Why this project exists

Small open-source teams often have the same responsibilities as large engineering organisations but without dedicated triage, security, release, or developer-relations staff. Existing tools are frequently narrow, hosted-only, or capable of making changes before a maintainer has reviewed the evidence. TriageForge produces reviewable reports and leaves every consequential action to a human.

## Install

```bash
python -m pip install .
triageforge audit .
```

For optional OpenAI analysis:

```bash
python -m pip install '.[ai]'
export OPENAI_API_KEY='your-key'
triageforge issue --title 'Windows crash' --body '...' --ai
```

The model can be changed with `--model` or `TRIAGEFORGE_MODEL`. API requests use `store=False`.

## Commands

### Repository audit

```bash
triageforge audit .
triageforge audit . --json
triageforge audit . --fail-under 80
```

### Issue triage and duplicate detection

```bash
triageforge issue \
  --title 'CLI crashes on Windows startup' \
  --body 'Version 1.2.0 fails on Windows 11. Steps: ...' \
  --issues-json examples/issues.json
```

### Pull-request risk

```bash
triageforge pr . --base origin/main --head HEAD
```

Risk signals include large diffs, authentication and permission code, migrations, CI workflows, dependency locks, public interfaces, and missing tests.

### Release notes

```bash
triageforge release . --from-ref v0.1.0 --to-ref HEAD --output RELEASE_NOTES.md
```

## GitHub Action

```yaml
name: Maintainer report
on:
  issues:
    types: [opened, edited]
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

jobs:
  triageforge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - uses: theopensourcestudio/triageforge@v0.1.0
```

The action writes a report to the GitHub job summary. It does not comment, label, close, approve, or merge anything by default.

## Design principles

1. **Human authority:** recommendations are not actions.
2. **Local-first:** core functionality requires no network or account.
3. **Explainability:** every risk score includes evidence and next checks.
4. **Safe handling of untrusted text:** issue and repository content is treated as data.
5. **Low adoption cost:** no server, database, GitHub App, or paid API is required.
6. **Provider optionality:** the deterministic engine remains useful without AI.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src/triageforge
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), [ROADMAP.md](ROADMAP.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and the [publishing checklist](docs/PUBLISHING.md).

## Maintainer

TriageForge is initiated and primarily maintained by [@theopensourcestudio](https://github.com/theopensourcestudio). Project decisions and maintainer responsibilities are documented in [GOVERNANCE.md](GOVERNANCE.md).

## Project status

TriageForge is an early public alpha. The first goal is to validate the reports on real repositories and collect false-positive examples before enabling any optional write integrations.

## Licence

MIT. See [LICENSE](LICENSE).
