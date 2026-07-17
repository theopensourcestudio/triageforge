# Security policy

## Supported versions

Only the latest released minor version receives security fixes during the alpha stage.

## Reporting a vulnerability

Use GitHub's private security advisory form for this repository. Do not open a public issue containing an exploit, secret, private repository content, or personal data.

Include the affected version, impact, minimal reproduction, prerequisites, and a safe remediation suggestion where available. Maintainers will acknowledge credible reports as capacity permits and coordinate disclosure after a fix is available.

## Security boundaries

TriageForge is read-only by default. It analyses local files, git metadata, and explicit event payloads. Optional OpenAI requests require explicit `--ai` use and an API key; requests set `store=False`. Users remain responsible for deciding whether repository material may be sent to an external API.
