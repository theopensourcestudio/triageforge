# Roadmap

## 0.1 — Useful local core

- repository health audit;
- deterministic issue labels and evidence checks;
- offline duplicate suggestions;
- git-diff pull-request risk report;
- release-note generation;
- read-only GitHub Action;
- optional OpenAI second opinion.

## 0.2 — Adoption and evaluation

- publish a labelled benchmark of real, anonymised issue examples;
- measure duplicate precision and triage false-positive rates;
- support repository-owned configuration;
- add SARIF and stable JSON schemas;
- add GitLab-compatible event input;
- publish an adoption guide and example integrations.

## 0.3 — Maintainer-controlled integrations

- optional draft comments that still require workflow-level permission;
- label mapping with explicit allowlists;
- release-note comparison against merged pull requests;
- plugin interface for ecosystem-specific rules.

## Non-goals

- autonomous merging, closing, publishing, or security remediation;
- replacing maintainer judgement;
- scraping private repositories without authorisation;
- claiming a vulnerability is valid without reproducible evidence.
