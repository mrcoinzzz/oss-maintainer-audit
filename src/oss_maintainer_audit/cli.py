from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import AuditResult, CheckResult, audit_repository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="oss-maintainer-audit",
        description="Audit a repository for public open-source maintenance signals.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository path to audit")
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format",
    )
    parser.add_argument("--min-score", type=int, default=70, help="Minimum passing score percentage")
    parser.add_argument("--output", help="Write the audit report to a file")
    parser.add_argument("--failures-only", action="store_true", help="Only include failing checks in the report output")

    args = parser.parse_args(argv)

    try:
        result = audit_repository(Path(args.path))
    except (FileNotFoundError, NotADirectoryError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.format == "json":
        output = _to_json(result, args.failures_only)
    elif args.format == "markdown":
        output = _to_markdown(result, args.min_score, args.failures_only)
    else:
        output = _to_text(result, args.min_score, args.failures_only)

    if args.output:
        try:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output + "\n", encoding="utf-8")
        except OSError as error:
            print(f"Could not write audit report: {error}", file=sys.stderr)
            return 2
    else:
        print(output)

    return 0 if result.score_percent >= args.min_score else 1


def _to_text(result: AuditResult, min_score: int, failures_only: bool = False) -> str:
    lines = [
        f"OSS Maintainer Audit: {result.root}",
        "",
        f"Score: {result.passed}/{result.total} ({result.score_percent}%)",
        f"Required: {min_score}%",
        "",
    ]

    checks = _report_checks(result, failures_only)
    if not checks:
        lines.append("All checks passed.")

    for check in checks:
        status = "PASS" if check.passed else "WARN"
        lines.append(f"{status:<5} {check.name:<22} {check.message}")

    return "\n".join(lines)


def _to_json(result: AuditResult, failures_only: bool = False) -> str:
    payload = {
        "root": str(result.root),
        "score": {
            "passed": result.passed,
            "total": result.total,
            "percent": result.score_percent,
        },
        "failures_only": failures_only,
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
                "weight": check.weight,
            }
            for check in _report_checks(result, failures_only)
        ],
    }
    return json.dumps(payload, indent=2)


def _to_markdown(result: AuditResult, min_score: int, failures_only: bool = False) -> str:
    lines = [
        "# OSS Maintainer Audit",
        "",
        f"Repository: `{result.root}`",
        "",
        f"Score: **{result.passed}/{result.total} ({result.score_percent}%)**",
        f"Required: **{min_score}%**",
        "",
        "| Status | Check | Detail |",
        "| --- | --- | --- |",
    ]

    checks = _report_checks(result, failures_only)
    if not checks:
        lines.append("| PASS | All checks | All checks passed. |")

    for check in checks:
        status = "PASS" if check.passed else "WARN"
        lines.append(f"| {status} | {check.name} | {check.message} |")

    return "\n".join(lines)


def _report_checks(result: AuditResult, failures_only: bool) -> tuple[CheckResult, ...]:
    if not failures_only:
        return result.checks
    return tuple(check for check in result.checks if not check.passed)


if __name__ == "__main__":
    raise SystemExit(main())
