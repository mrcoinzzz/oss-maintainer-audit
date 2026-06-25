# OSS Maintainer Audit

A small command line tool for checking whether an open-source repository has the public maintenance signals contributors, users, and reviewers usually look for.

It is designed for maintainers who want a quick, plain-English checklist before publishing a project, applying for OSS support programs, or improving contributor experience.

## What it checks

- README presence and basic usefulness
- License file
- Contributing guide
- Code of conduct
- Security policy
- Issue templates
- Pull request template
- CI workflow
- Release notes or changelog
- Package metadata

The tool works on a local repository path and does not need network access.

## Install

Clone the repository, then run:

```bash
python3 -m pip install -e .
```

## Usage

Audit the current directory:

```bash
oss-maintainer-audit
```

Audit another repository:

```bash
oss-maintainer-audit /path/to/project
```

Show JSON output:

```bash
oss-maintainer-audit /path/to/project --format json
```

Generate a Markdown report:

```bash
oss-maintainer-audit /path/to/project --format markdown
```

Write a report to a file:

```bash
oss-maintainer-audit /path/to/project --format markdown --output audit-report.md
```

Use a custom CI threshold:

```bash
oss-maintainer-audit /path/to/project --min-score 80
```

Show only missing maintainer signals:

```bash
oss-maintainer-audit /path/to/project --failures-only
```

This repository includes an example workflow at `.github/workflows/audit-report.yml` that writes a Markdown maintainer audit report to the GitHub Actions step summary.

## Example

```text
OSS Maintainer Audit: /path/to/project

Score: 8/10

PASS  README                 README.md found
PASS  License                LICENSE found
WARN  Security policy         Add SECURITY.md or .github/SECURITY.md
```

## Why this exists

Maintainers often carry invisible work: review, triage, release management, user support, documentation, and security response. This tool helps make some of that work visible and gives small projects a practical checklist for becoming easier to trust and contribute to.

## Roadmap

- GitHub URL auditing through the public API
- Suggested fixes for missing files
- Configurable checks
- Score history for release readiness

## License

MIT
