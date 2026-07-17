# Publishing checklist

This document records the repeatable release process for the primary maintainer.

## First public release

1. Create a public GitHub repository named `triageforge` under `theopensourcestudio`.
2. Push the complete repository to the `main` branch.
3. Enable GitHub Discussions, Issues, Actions, Dependabot alerts, private vulnerability reporting, and branch protection.
4. Require every Python-version check from the `CI` workflow before merging to `main`.
5. Confirm the repository Action passes on `main`.
6. Create and push the annotated tag `v0.1.0`.
7. Publish release notes from `CHANGELOG.md`.
8. Test installation in a fresh environment.
9. Test the Action in at least one separate public repository.

## Release commands

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src/triageforge
python -m build

git tag -a v0.1.0 -m "TriageForge v0.1.0"
git push origin main --follow-tags
```

## Evidence to retain

For future programme or grant applications, retain links to public releases, resolved issues, reviewed pull requests, external repositories using the Action, package download statistics, security fixes, contributor activity, and published roadmap updates. Record only genuine public evidence.
