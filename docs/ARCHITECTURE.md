# Architecture

TriageForge is deliberately small and separable.

1. **Collectors** read explicit local inputs: repository paths, git diffs, JSON issue lists, and GitHub event payloads.
2. **Deterministic analysers** calculate repository findings, token similarity, issue labels, missing evidence, and pull-request risk.
3. **Optional AI enrichment** receives a bounded textual report only after the user passes `--ai`. Repository text is framed as untrusted data, storage is disabled, and the output is advisory.
4. **Formatters** emit Markdown or JSON for terminals, CI logs, and GitHub job summaries.
5. **Action wrapper** installs the checked-out package and runs the same CLI; there is no separate hosted service.

The project does not need a database. This lowers operational burden and allows maintainers to inspect exactly what runs in their repository.

## Trust boundaries

Issue bodies, commit messages, filenames, and repository files may contain prompt injection, escape sequences, malformed text, or deliberately misleading claims. They are never executed. Optional AI prompts state that embedded instructions are data. Future write integrations must use explicit allowlists and remain off by default.
